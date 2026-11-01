/* ================= Soru üreticileri (kazanımlara göre) ================= */
function q(text, answer, wrong, why) {
  const opts = [String(answer)];
  for (const w of wrong) { const s = String(w); if (!opts.includes(s) && opts.length < 4) opts.push(s); }
  let guard = 0;
  while (opts.length < 4 && guard++ < 20) { const n = String(rnd(1, 40)); if (!opts.includes(n)) opts.push(n); }
  return { text, answer: String(answer), options: shuffle(opts), why };
}

const LEVELS6 = [
  {
    title: 'Sözelden cebire',
    kaz: 'MAT.6.2.1 · Nicelikler arasındaki ilişkileri cebirsel olarak ifade eder.',
    text: 'Günlük hayattaki durumları cebirsel ifadeye çevir. Bilinmeyen niceliği bir harfle göster.',
    gen: [
      () => { const v = pick(VARS), k = rnd(3, 15);
        return q(`Ahmet'in parası ${v} TL. Mehmet'in parası Ahmet'inkinden ${k} TL fazla. Mehmet'in parası?`,
          `${v} + ${k}`, [`${v} − ${k}`, `${k}${v}`, `${k} − ${v}`], `"${k} TL fazla" → ${v} + ${k}`); },
      () => { const v = pick(VARS), k = rnd(3, 15);
        return q(`Mehmet'in parası ${v} TL ve Ahmet'inkinden ${k} TL fazla. Ahmet'in parası?`,
          `${v} − ${k}`, [`${v} + ${k}`, `${k} − ${v}`, `${k}${v}`], `Mehmet ${k} TL fazlaysa Ahmet ${k} TL eksik: ${v} − ${k}`); },
      () => { const v = pick(VARS), k = rnd(2, 9);
        return q(`Bir defterin fiyatı ${v} TL. ${k} defter kaç TL?`,
          `${k}${v}`, [`${v} + ${k}`, `${v}/${k}`, `${v} − ${k}`], `${k} tane ${v} → ${k}·${v} = ${k}${v}`); },
      () => { const v = pick(VARS), k = rnd(2, 8);
        return q(`${k} arkadaş ${v} tane cevizi eşit paylaşıyor. Birine kaç ceviz düşer?`,
          `${v}/${k}`, [`${k}${v}`, `${v} − ${k}`, `${k}/${v}`], `Eşit paylaşma bölmedir: ${v}/${k}`); },
      () => { const v = pick(VARS), k = rnd(2, 6), m = rnd(1, 9);
        return q(`"Bir sayının ${k} katının ${m} fazlası" cebirsel ifadesi hangisi?`,
          `${k}${v} + ${m}`, [`${k}(${v} + ${m})`, `${m}${v} + ${k}`, `${k}${v} − ${m}`], `Önce ${k} katı (${k}${v}), sonra ${m} fazlası: ${k}${v} + ${m}`); },
      () => { const v = pick(VARS), k = rnd(2, 6), m = rnd(1, 9);
        return q(`"Bir sayının ${m} fazlasının ${k} katı" cebirsel ifadesi hangisi?`,
          `${k}(${v} + ${m})`, [`${k}${v} + ${m}`, `${m}(${v} + ${k})`, `${k}${v} − ${m}`], `Önce ${m} fazlası (${v} + ${m}), sonra ${k} katı: ${k}(${v} + ${m})`); },
      () => { const v = pick(VARS), k = rnd(2, 9);
        return q(`Zeynep ${v} yaşında. Kardeşi ondan ${k} yaş küçük. Kardeşi kaç yaşında?`,
          `${v} − ${k}`, [`${v} + ${k}`, `${k} − ${v}`, `${k}${v}`], `"${k} yaş küçük" → ${v} − ${k}`); },
      () => { const s = rnd(6, 12), a = rnd(3, 8); if (s === a) return LEVELS6[0].gen[0]();
        return q(`Simidin tanesi ${s} TL, ayranın tanesi ${a} TL. m simit ve n ayran kaç TL?`,
          `${s}m + ${a}n`, [`${a}m + ${s}n`, `${s + a}mn`, `${s}m + n`], `m simit: ${s}m, n ayran: ${a}n → ${s}m + ${a}n`); },
      () => q(`Kenar uzunlukları x ve y birim olan dikdörtgenin çevre uzunluğu?`,
          `2x + 2y`, [`x + y`, `2x + y`, `4xy`], `İki tane x, iki tane y kenar: 2x + 2y`),
    ]
  },
  {
    title: 'Denk ifadeler',
    kaz: 'MAT.6.2.1 · Cebirsel ifadelere denk ifadeler oluşturur; katsayı, sabit terim ve terimi yorumlar.',
    text: 'Aynı anlama gelen ifadeleri bul. Katsayı, sabit terim ve terim sayısını hatırla.',
    gen: [
      () => { const v = pick(VARS), k = rnd(3, 7), p = rnd(1, k - 1);
        const right = pick([`${coef(p, v)} + ${coef(k - p, v)}`, `${v}·${k}`, `${v}${k}`]);
        return q(`${k}${v} ifadesine denk olan hangisi?`, right,
          [`${k} + ${v}`, `${v} − ${k}`, `${k}${v} + ${k}`], `${k}${v}, ${k} tane ${v}'nin toplamıdır. ${right} de ${k} tane ${v} eder.`); },
      () => { const v = pick(VARS), k = rnd(2, 5), m = rnd(1, 6);
        return q(`${k}(${v} + ${m}) ifadesine denk olan hangisi?`,
          `${k}${v} + ${k * m}`, [`${k}${v} + ${m}`, `${v} + ${k * m}`, `${k + m}${v}`], `${k} ile hem ${v}'yi hem ${m}'yi çarp: ${k}${v} + ${k * m}`); },
      () => { const v = pick(VARS), k = rnd(2, 9); let m = rnd(1, 9); if (m === k) m++;
        return q(`${k}${v} + ${m} ifadesinde ${v}'nin katsayısı kaçtır?`,
          k, [m, k + m, k * m], `Harfin önündeki sayı katsayıdır: ${k}`); },
      () => { const v = pick(VARS), k = rnd(2, 9); let m = rnd(1, 9); if (m === k) m++;
        return q(`${k}${v} + ${m} ifadesinde sabit terim kaçtır?`,
          m, [k, k + m, k * m], `Harfi olmayan terim sabit terimdir: ${m}`); },
      () => { const a = rnd(2, 6), b = rnd(2, 6), c = rnd(1, 9);
        return q(`${a}x + ${b}y + ${c} ifadesinde kaç terim vardır?`,
          3, [2, 4, 5], `${a}x, ${b}y ve ${c} → 3 terim`); },
      () => { const v = pick(VARS);
        return q(`${v} + ${v} + ${v} ifadesinin kısa yazılışı hangisi?`,
          `3${v}`, [`${v} + 3`, `3 + ${v}`, `6${v}`], `3 tane ${v} → 3${v}`); },
      () => { const v = pick(VARS), k = rnd(2, 6);
        return q(`${coef(k, v)} + ${v} ifadesine denk olan hangisi?`,
          `${k + 1}${v}`, [`${k}${v}`, `${k + 1} + ${v}`, `${k}${v} + 1`], `${k} tane ${v} ile 1 tane ${v}: ${k + 1}${v}`); },
    ]
  },
  {
    title: 'Örüntüler',
    kaz: 'MAT.6.2.2 · Örüntülerdeki yapıları cebirsel olarak ifade eder.',
    text: 'Sayı örüntülerinin kuralını bul. Kuralı kullanarak istenen adımdaki terimi hesapla.',
    gen: [
      () => { const d = rnd(2, 6), a0 = rnd(1, 9), c = a0 - d; const seq = [0, 1, 2, 3].map(i => a0 + i * d).join(', ');
        const rule = `${d}n${sgn(c)}`;
        return q(`Örüntü: ${seq}, … n. adımdaki terimin kuralı nedir?`, rule,
          [`${d}n${sgn(a0)}`, `n${sgn(d)}`, `${a0}n${sgn(d)}`], `Her adımda ${d} artıyor → ${d}n. 1. adımda ${a0} çıkması için: ${rule}`); },
      () => { const d = rnd(2, 6), a0 = rnd(1, 9), c = a0 - d, s = rnd(6, 12); const seq = [0, 1, 2, 3].map(i => a0 + i * d).join(', ');
        const val = d * s + c;
        return q(`Örüntü: ${seq}, … ${s}. adımdaki terim kaçtır?`, val,
          [val + d, val - d, d * s], `Kural ${d}n${sgn(c)} → ${d}·${s}${sgn(c)} = ${val}`); },
      () => { const d = rnd(2, 5), c = rnd(-1, 4); const t = [1, 2, 3].map(n => d * n + c);
        return q(`Kuralı ${d}n${sgn(c)} olan örüntünün ilk 3 terimi hangisi?`, t.join(', '),
          [[0, 1, 2].map(n => d * n + c).join(', '), [1, 2, 3].map(n => d + n + c).join(', '), [2, 3, 4].map(n => d * n + c).join(', ')],
          `n = 1, 2, 3 yaz: ${t.join(', ')}`); },
      () => q(`Üçgen 180°, dörtgen 360°, beşgen 540°… n kenarlı çokgenin iç açıları toplamı?`,
          `(n − 2)·180°`, [`n·180°`, `(n − 1)·180°`, `n·360°`], `Çokgen (n − 2) üçgene bölünür: (n − 2)·180°`),
      () => { const n = pick([3, 4, 5, 6, 8, 9, 10, 12]);
        return q(`Düzgün ${n}-genin bir dış açısı kaç derecedir?`, 360 / n,
          [180 / n * 2 + 10, (n - 2) * 180 / n, 360 / n + 10], `Dış açı = 360° ÷ ${n} = ${360 / n}°`); },
    ]
  },
  {
    title: 'Algoritma ve değer',
    kaz: 'MAT.6.2.3 · Cebirsel ifadeler içeren algoritmaları yorumlar.',
    text: 'Adımları sırayla uygula. Harfin yerine sayıyı koyarak ifadenin değerini bul.',
    gen: [
      () => { const v = pick(VARS), k = rnd(2, 6), m = rnd(1, 9), x = rnd(2, 9);
        return q(`${v} = ${x} için ${k}${v} + ${m} ifadesinin değeri kaçtır?`, k * x + m,
          [k + x + m, k * (x + m), k * x - m], `${k}·${x} + ${m} = ${k * x} + ${m} = ${k * x + m}`); },
      () => { const k = rnd(2, 5), m = rnd(1, 9), x = rnd(2, 9);
        return q(`Algoritma: 1) Bir sayı al  2) ${k} ile çarp  3) ${m} ekle  4) Sonucu yaz. Sayı ${x} ise sonuç?`, k * x + m,
          [(x + m) * k, k * x - m, x + k + m], `${x}·${k} = ${k * x}, sonra + ${m} = ${k * x + m}`); },
      () => { const k = rnd(2, 5), m = rnd(1, 9), x = rnd(2, 9), r = k * x + m;
        return q(`Aklından bir sayı tut, ${k} ile çarp, ${m} ekle. Sonuç ${r}. Tuttuğun sayı kaç?`, x,
          [x + 1, r - m, x - 1], `Tersine git: ${r} − ${m} = ${r - m}, ${r - m} ÷ ${k} = ${x}`); },
      () => { const k = rnd(2, 5), m = rnd(1, 7);
        return q(`Algoritma: sayıyı al, ${m} ekle, ${k} ile çarp. Bu algoritmanın cebirsel ifadesi hangisi?`,
          `${k}(x + ${m})`, [`${k}x + ${m}`, `${m}(x + ${k})`, `x + ${k * m}`], `Önce ekleme (x + ${m}), sonra çarpma: ${k}(x + ${m})`); },
      () => { const v = pick(VARS), k = rnd(2, 5), m = rnd(1, 4), x = rnd(m + 1, 10);
        return q(`${v} = ${x} için ${k}(${v} − ${m}) ifadesinin değeri kaçtır?`, k * (x - m),
          [k * x - m, k * (x + m), x - m], `${k}·(${x} − ${m}) = ${k}·${x - m} = ${k * (x - m)}`); },
    ]
  }
];
const PER_LEVEL = 5;