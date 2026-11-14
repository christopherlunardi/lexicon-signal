// Music workshop, round 1 (Chris 2026-11-14): chill 1930s-40s jazz, low and smooth, as if a band were playing in the next room.
// Everything is synthesized with Web Audio (no recordings), so it costs a few oscillators at a time and loops forever.
// jazzSchedule(ac, out, style, t0, t1, st) schedules the notes that start between t0 and t1 (call it again for the next window);
// jazzChain(ac, style) builds the "next room" chain (filter, reverb, the record's crackle) and returns { input, output }.
(function () {
  const m2f = (m) => 440 * Math.pow(2, (m - 69) / 12);
  function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  // chords: root (midi), a rootless voicing (semitones above the root, played in the piano's middle), and the scale for lines
  const Q = { m9: [3, 7, 10, 14], m11: [3, 10, 14, 17], d13: [4, 10, 14, 21], d9: [4, 10, 14, 19], d7b9: [4, 10, 13, 19], d7b13: [4, 10, 13, 20], M9: [4, 7, 11, 14], M69: [4, 9, 14, 19], m7b5: [3, 6, 10, 14], m6: [3, 7, 9, 14] };
  const SC = { m: [0, 2, 3, 5, 7, 9, 10], d: [0, 2, 4, 5, 7, 9, 10], M: [0, 2, 4, 5, 7, 9, 11], h: [0, 1, 3, 5, 6, 8, 10], alt: [0, 1, 3, 4, 6, 8, 10] };
  const C = (root, q, sc, beats) => ({ root, v: Q[q], sc: SC[sc], beats });
  // progressions, one entry per chord (beats it lasts)
  const PROG = {
    // a slow minor ballad in D minor: i - IV7 - bVImaj - V7, then a turnaround
    ballad: [C(38, "m9", "m", 4), C(43, "d13", "d", 4), C(46, "M9", "M", 4), C(45, "d7b13", "alt", 4), C(38, "m9", "m", 4), C(43, "d13", "d", 4), C(40, "m7b5", "h", 2), C(45, "d7b9", "alt", 2), C(38, "m6", "m", 2), C(45, "d7b13", "alt", 2)],
    // a Bb swing tune's changes: I - VI7 - ii - V, iii - VI, ii - V
    swing: [C(46, "M69", "M", 4), C(43, "d7b9", "alt", 4), C(48, "m9", "m", 4), C(41, "d13", "d", 4), C(38, "m11", "m", 2), C(43, "d7b13", "alt", 2), C(48, "m9", "m", 2), C(41, "d13", "d", 2), C(46, "M9", "M", 4), C(39, "d9", "d", 4), C(38, "m11", "m", 2), C(43, "d7b9", "alt", 2), C(48, "m9", "m", 2), C(41, "d13", "d", 2)],
    // slow, open Eb: Imaj - IVmaj - iii - VI7 - ii - V
    dream: [C(39, "M9", "M", 8), C(44, "M69", "M", 8), C(43, "m9", "m", 4), C(36, "d7b13", "alt", 4), C(41, "m9", "m", 4), C(46, "d13", "d", 4)],
  };

  const STYLES = {
    // 1: piano trio, ballad, brushes, upright bass
    trio:   { bpm: 70, prog: "ballad", piano: 1, bass: 1, brush: 1, ride: .5, lead: "piano", lp: 2200, wet: .32, level: .9, seed: 7 },
    // 2: a small band swinging, a muted horn taking the tune now and then
    horn:   { bpm: 96, prog: "swing", piano: .8, bass: 1, brush: 1, ride: 1, lead: "horn", lp: 2000, wet: .3, level: .85, seed: 11 },
    // 3: the trio on an old 78 heard through the wall: narrow, warm, crackling, the record wavering
    record: { bpm: 84, prog: "swing", piano: 1, bass: 1, brush: .9, ride: .7, lead: "clar", lp: 2600, hp: 300, wet: .22, level: .95, crackle: 1, wow: 1, seed: 21 },
    // 4: vibraphone after hours, bass and the softest brushes, very slow
    vibes:  { bpm: 62, prog: "dream", piano: .45, bass: .9, brush: .55, ride: 0, lead: "vibes", lp: 2400, wet: .4, level: .9, seed: 5 },
  };

  let NB = null;
  function noiseBuf(ac) { if (NB && NB.sampleRate === ac.sampleRate) return NB; NB = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate); const d = NB.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; return NB; }

  // ---- instruments: each one note, a handful of nodes, stopped as soon as it is silent ----
  function piano(ac, out, m, t, vel, len) {   // a felt-damped upright: a few sine partials, a soft hammer, a gentle decay
    const f = m2f(m), g = ac.createGain(), lp = ac.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.setValueAtTime(900 + vel * 1800, t); lp.frequency.exponentialRampToValueAtTime(500, t + 1.2); g.connect(lp); lp.connect(out);
    const dec = Math.min(len + .4, 2.6);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .11, t + .006); g.gain.exponentialRampToValueAtTime(vel * .045, t + .25); g.gain.setTargetAtTime(.0001, t + len, .25); g.gain.exponentialRampToValueAtTime(.00005, t + dec + .3);
    [[1, 1, 0], [2, .32, 3], [3, .1, -4], [4, .05, 2]].forEach(([k, a, det]) => { const o = ac.createOscillator(), og = ac.createGain(); o.type = "sine"; o.frequency.value = f * k; o.detune.value = det; og.gain.value = a; o.connect(og); og.connect(g); o.start(t); o.stop(t + dec + .35); });
  }
  function bass(ac, out, m, t, vel, len) {   // upright: a round thump that blooms then dies, a little string buzz on top
    const f = m2f(m), g = ac.createGain(), lp = ac.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.setValueAtTime(700, t); lp.frequency.exponentialRampToValueAtTime(260, t + .3); lp.Q.value = 1.5; g.connect(lp); lp.connect(out);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .34, t + .012); g.gain.exponentialRampToValueAtTime(vel * .15, t + .12); g.gain.exponentialRampToValueAtTime(.0001, t + Math.max(.3, len * 1.1));
    const o = ac.createOscillator(); o.type = "triangle"; o.frequency.setValueAtTime(f * 1.012, t); o.frequency.exponentialRampToValueAtTime(f, t + .05); o.connect(g); o.start(t); o.stop(t + len * 1.1 + .1);
    const s = ac.createOscillator(), sg = ac.createGain(); s.type = "sine"; s.frequency.value = f; sg.gain.value = .8; s.connect(sg); sg.connect(g); s.start(t); s.stop(t + len * 1.1 + .1);
  }
  function brush(ac, out, t, vel, dur) {   // a brush swept across the snare head: filtered noise swelling and fading
    const s = ac.createBufferSource(); s.buffer = noiseBuf(ac); const bp = ac.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 3200; bp.Q.value = .6; const g = ac.createGain();
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .05, t + dur * .45); g.gain.exponentialRampToValueAtTime(.0001, t + dur); s.connect(bp); bp.connect(g); g.connect(out); s.start(t, Math.random() * 1.5); s.stop(t + dur + .05);
  }
  function tap(ac, out, t, vel) {   // the brush slapped on 2 and 4
    const s = ac.createBufferSource(); s.buffer = noiseBuf(ac); const bp = ac.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 2200; bp.Q.value = .9; const g = ac.createGain();
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .09, t + .004); g.gain.exponentialRampToValueAtTime(.0001, t + .16); s.connect(bp); bp.connect(g); g.connect(out); s.start(t, Math.random() * 1.5); s.stop(t + .2);
  }
  function ride(ac, out, t, vel) {   // a ride cymbal, tapped lightly
    const s = ac.createBufferSource(); s.buffer = noiseBuf(ac); const hp = ac.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 6500; const g = ac.createGain();
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .03, t + .003); g.gain.exponentialRampToValueAtTime(.0001, t + .5); s.connect(hp); hp.connect(g); g.connect(out); s.start(t, Math.random() * 1.5); s.stop(t + .55);
    const o = ac.createOscillator(), og = ac.createGain(); o.type = "square"; o.frequency.value = 5200; og.gain.setValueAtTime(vel * .004, t); og.gain.exponentialRampToValueAtTime(.00005, t + .35); o.connect(og); og.connect(out); o.start(t); o.stop(t + .4);
  }
  function kick(ac, out, t, vel) {   // the bass drum feathered on every beat, felt more than heard
    const o = ac.createOscillator(), g = ac.createGain(); o.type = "sine"; o.frequency.setValueAtTime(90, t); o.frequency.exponentialRampToValueAtTime(48, t + .12);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .05, t + .006); g.gain.exponentialRampToValueAtTime(.0001, t + .2); o.connect(g); g.connect(out); o.start(t); o.stop(t + .25);
  }
  function lead(ac, out, kind, m, t, vel, len) {
    const f = m2f(m), g = ac.createGain(); g.connect(out);
    if (kind === "piano") { piano(ac, out, m, t, vel * 1.1, len); return; }
    if (kind === "vibes") {   // vibraphone: a bar ringing with the motor's slow tremolo
      g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vel * .12, t + .004); g.gain.exponentialRampToValueAtTime(.0001, t + Math.max(1.6, len + 1.2));
      const trem = ac.createGain(), lfo = ac.createOscillator(), lg = ac.createGain(); trem.gain.value = .75; lfo.frequency.value = 5.2; lg.gain.value = .25; lfo.connect(lg); lg.connect(trem.gain); trem.connect(g); lfo.start(t); lfo.stop(t + len + 1.5);
      [[1, 1], [4, .12], [10, .03]].forEach(([k, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.type = "sine"; o.frequency.value = f * k; og.gain.setValueAtTime(a, t); og.gain.exponentialRampToValueAtTime(.001, t + (k > 1 ? .4 : len + 1.4)); o.connect(og); og.connect(trem); o.start(t); o.stop(t + len + 1.5); });
      return; }
    // horn (cup-muted trumpet) or clarinet: a reed-ish wave through a soft filter, with a breathy start and a slow vibrato
    const o = ac.createOscillator(), lp = ac.createBiquadFilter(), vib = ac.createOscillator(), vg = ac.createGain();
    o.type = kind === "clar" ? "square" : "sawtooth"; o.frequency.setValueAtTime(f * .985, t); o.frequency.exponentialRampToValueAtTime(f, t + .06);
    vib.frequency.value = 4.8; vg.gain.setValueAtTime(0, t); vg.gain.linearRampToValueAtTime(f * .006, t + Math.min(len, .5)); vib.connect(vg); vg.connect(o.frequency);
    lp.type = kind === "clar" ? "lowpass" : "bandpass"; lp.frequency.value = kind === "clar" ? 1300 : 1100; lp.Q.value = kind === "clar" ? .7 : 1.4;
    const pk = vel * (kind === "clar" ? .05 : .085);
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(pk, t + .05); g.gain.setValueAtTime(pk, t + Math.max(.06, len - .08)); g.gain.exponentialRampToValueAtTime(.0001, t + len + .18);
    o.connect(lp); lp.connect(g); o.start(t); o.stop(t + len + .25); vib.start(t); vib.stop(t + len + .25);
  }

  // ---- the band: what each player does in each beat ----
  function chordAt(prog, beat) { const tot = prog.reduce((s, c) => s + c.beats, 0); let b = ((beat % tot) + tot) % tot; for (const c of prog) { if (b < c.beats) return { c, into: b, next: prog[(prog.indexOf(c) + 1) % prog.length] }; b -= c.beats; } }
  function nearest(m, target) { return m + Math.round((target - m) / 12) * 12; }
  function scaleNotes(c, lo, hi) { const out = []; for (let m = lo; m <= hi; m++) if (c.sc.includes(((m - c.root) % 12 + 12) % 12)) out.push(m); return out; }

  function jazzSchedule(ac, out, styleId, t0, t1, st) {
    const S = STYLES[styleId], beat = 60 / S.bpm, prog = PROG[S.prog], R = st.r || (st.r = rng(S.seed)), sw = beat * 2 / 3;   // swung eighths: the "and" lands two thirds through the beat
    if (st.start == null) { st.start = t0; st.lastBass = prog[0].root; st.lead = null; }
    for (let n = Math.max(0, Math.ceil((t0 - st.start) / beat - 1e-6)); ; n++) {
      const t = st.start + n * beat; if (t >= t1) break;
      const { c, into, next } = chordAt(prog, n), bar = Math.floor(n / 4), inBar = n % 4, hum = () => (R() - .5) * .018;   // hum: players are a hair early or late
      // bass: walks in quarter notes (root on the chord's first beat, chord and scale tones after, a half step into the next chord)
      if (S.bass) { let m;
        if (into === 0) m = nearest(c.root, st.lastBass);
        else if (into === c.beats - 1) { const nr = nearest(next.root, st.lastBass); m = nr + (R() < .5 ? -1 : 1); }
        else { const opts = scaleNotes(c, 31, 50).filter(x => Math.abs(x - st.lastBass) <= 5 && x !== st.lastBass); m = opts.length ? opts[Math.floor(R() * opts.length)] : c.root; }
        if (S.prog === "dream" && into % 2 === 1) m = null;   // the slow one: half notes
        if (m != null) { while (m < 31) m += 12; while (m > 50) m -= 12; bass(ac, out.bass, m, t + hum(), S.bass * (inBar === 0 ? 1 : .85), S.prog === "dream" ? beat * 1.9 : beat * .95); st.lastBass = m; } }
      // drums: brushes sweep every beat, slapped on 2 and 4; a feathered bass drum; the ride's "ding, ding-a ding"
      if (S.brush) { brush(ac, out.drums, t, S.brush * (inBar % 2 ? .8 : 1), beat * .95); if (inBar % 2 === 1) tap(ac, out.drums, t + hum(), S.brush); kick(ac, out.drums, t, .5 * S.brush); }
      if (S.ride) { ride(ac, out.drums, t + hum(), S.ride * (inBar % 2 ? 1 : .7)); if (inBar % 2 === 1) ride(ac, out.drums, t + sw + hum(), S.ride * .55); }
      // piano: comps the chord in the middle of the keyboard, on a beat or the "and" before it, sparse and soft
      if (S.piano && (into === 0 ? R() < .9 : R() < .38)) { let at = into === 0 && R() < .4 ? t - beat + sw : t + (R() < .3 ? sw : 0); if (at < t0) at = t; const vel = S.piano * (.45 + R() * .25);
        const base = nearest(c.root, 52); c.v.forEach((iv, k) => { let m = base + iv; while (m > 72) m -= 12; while (m < 50) m += 12; piano(ac, out.keys, m, at + k * .008 + hum(), vel * (k === 3 ? .8 : 1), beat * (into === 0 ? 1.6 : .9)); }); }
      if (S.prog === "dream" && into === 0 && S.piano) piano(ac, out.keys, nearest(c.root, 40), t, S.piano * .5, beat * 3);
      // the tune: a lead plays a short phrase, rests a while, then plays again (chord tones on the strong beats, steps between)
      if (S.lead) {
        if (!st.lead && inBar === 0 && bar % 4 === (S.lead === "vibes" ? 0 : 2) && R() < .85) st.lead = { left: S.lead === "vibes" ? 8 : 6, m: nearest(c.root + c.v[1], S.lead === "vibes" ? 74 : 70) };
        if (st.lead) { const L = st.lead, notes = scaleNotes(c, 62, 84), ct = c.v.map(iv => ((c.root + iv) % 12));
          const hits = S.lead === "vibes" || S.lead === "piano" ? [[0, R() < .7], [sw, R() < .35]] : [[0, R() < .75], [sw, R() < .55]];
          hits.forEach(([off, on]) => { if (!on || L.left <= 0) return;
            const strong = off === 0, pool = notes.filter(x => Math.abs(x - L.m) <= (strong ? 4 : 2) && (!strong || ct.includes(x % 12)));
            const m = pool.length ? pool[Math.floor(R() * pool.length)] : L.m; L.m = m;
            const len = S.lead === "vibes" ? beat * (strong ? 1.4 : .6) : (strong ? sw : beat - sw) * (R() < .25 ? 2.6 : .95);
            lead(ac, out.lead, S.lead, m, t + off + hum(), .7 + R() * .3, len); L.left -= .5; });
          if (L.left <= 0) st.lead = null; }
      }
    }
  }

  // the room the music is in: a little reverb, the high end gone through the wall, and for the record its crackle and wobble
  function jazzChain(ac, styleId) {
    const S = STYLES[styleId], input = ac.createGain(), output = ac.createGain(); output.gain.value = S.level;
    const bus = { bass: ac.createGain(), drums: ac.createGain(), keys: ac.createGain(), lead: ac.createGain() };
    bus.bass.gain.value = 1; bus.drums.gain.value = .9; bus.keys.gain.value = 1; bus.lead.gain.value = .9; Object.values(bus).forEach(b => b.connect(input));
    let x = input;
    if (S.wow) { const d = ac.createDelay(.05), l = ac.createOscillator(), lg = ac.createGain(); d.delayTime.value = .012; l.frequency.value = .55; lg.gain.value = .0011; l.connect(lg); lg.connect(d.delayTime); l.start(); x.connect(d); x = d; }
    const lp = ac.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = S.lp; lp.Q.value = .5; x.connect(lp); x = lp;
    const hp = ac.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = S.hp || 70; x.connect(hp); x = hp;
    // a small room's reverb, made from decaying noise
    const len = Math.floor(ac.sampleRate * 1.8), ir = ac.createBuffer(2, len, ac.sampleRate); for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
    const cv = ac.createConvolver(); cv.buffer = ir; const wet = ac.createGain(), dry = ac.createGain(); wet.gain.value = S.wet; dry.gain.value = 1 - S.wet * .5; x.connect(cv); cv.connect(wet); wet.connect(output); x.connect(dry); dry.connect(output);
    if (S.crackle) { const n = ac.sampleRate * 4, b = ac.createBuffer(1, n, ac.sampleRate), d = b.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * .012; for (let k = 0; k < 90; k++) { const p = Math.floor(Math.random() * (n - 40)), a = (Math.random() < .15 ? .5 : .18) * (Math.random() < .5 ? -1 : 1); for (let j = 0; j < 30; j++) d[p + j] += a * Math.exp(-j / 4); }
      const s = ac.createBufferSource(); s.buffer = b; s.loop = true; const f = ac.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = 2400; f.Q.value = .5; const g = ac.createGain(); g.gain.value = .35; s.connect(f); f.connect(g); g.connect(output); s.start(); }
    return { input, output, bus };
  }

  window.JAZZ = { STYLES, jazzSchedule, jazzChain };
})();
