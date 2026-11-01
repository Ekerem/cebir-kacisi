/* ================= 5. sınıf soruları (2. Tema: İşlemlerle Cebirsel Düşünme) =================
   Her bölüm kolaydan zora: t = 1 kolay, 2 orta, 3 zor. Bölümün 1-2. soruları kolay, 3-4. orta, 5. zor gelir. */
const LEVELS5 = [
  {
    title: 'Eşitlik ve işlem özellikleri', tiered: true,
    kaz: 'MAT.5.2.1 · Eşitliğin korunumuna ve işlem özelliklerine yönelik çıkarım yapar.',
    text: 'Eşittir işaretinin iki tarafı dengede olmalı, tıpkı bir terazi gibi.',
    gen: [
      { t: 1, f: () => { const a = rnd(2, 9), b = rnd(2, 9); if (a === b) return LEVELS5[0].gen[1].f();
        return q(`${a} + ${b} = ${b} + ?`, a, [b, a + b, a + 1], `Toplananların yeri değişse de toplam aynı kalır.`); } },
      { t: 1, f: () => { const a = rnd(2, 9), b = rnd(2, 5); if (a === b) return LEVELS5[0].gen[0].f();
        return q(`${a} × ${b} = ${b} × ?`, a, [b, a * b, a + b], `Çarpanların yeri değişse de çarpım aynı kalır.`); } },
      { t: 1, f: () => { const a = rnd(2, 6), b = rnd(2, 6);
        return q(`Terazinin bir kefesinde ${a} + ${b}, diğerinde ? var. Terazi dengede. ? kaç?`, a + b, [a + b + 1, a * b === a + b ? a + b + 2 : a * b, Math.max(a, b)], `Dengede ise iki taraf eşit: ${a} + ${b} = ${a + b}`); } },
      { t: 2, f: () => { const a = rnd(5, 12), b = rnd(3, 9);
        return q(`${a} + ${b} = ${a - 1} + ?`, b + 1, [b, b - 1, a + 1], `Birinci sayı 1 azaldı, ikinci sayı 1 artmalı: ${b} + 1 = ${b + 1}`); } },
      { t: 2, f: () => { const a = rnd(2, 6), b = rnd(2, 6), L = a + b, c = L + rnd(1, 4), e = rnd(1, 5);
        return q(`${a} + ${b} = ${c} − ${c - L} ise ${a} + ${b} + ${e} = ${c} − ${c - L} + ?`, e, [e + 1, L, c], `İki tarafa da aynı sayı eklenirse eşitlik bozulmaz: + ${e}`); } },
      { t: 2, f: () => { const a = rnd(2, 5), b = rnd(2, 5), c = pick([2, 5, 10]);
        return q(`(${a} × ${b}) × ${c} = ${a} × (${b} × ?)`, c, [a, b, a * b], `Çarpanları farklı gruplasak da çarpım değişmez.`); } },
      { t: 3, f: () => { const a = rnd(2, 6), c = rnd(1, 5);
        return q(`${a} × (10 + ${c}) = ${a} × 10 + ${a} × ?`, c, [10, a, 10 + c], `${a}, parantezdeki iki sayıyla ayrı ayrı çarpılır: ${a} × 10 + ${a} × ${c}`); } },
      { t: 3, f: () => { const a = rnd(2, 5), p = rnd(2, 5), c = rnd(2, 4);
        return q(`Bir pakette ${p} kalem, bir kutuda ${a} paket, bir kolide ${c} kutu var. Bir kolide kaç kalem var?`, p * a * c, [p + a + c, p * a, a * c === p * a ? p * a * c + p : a * c], `(${p} × ${a}) × ${c} = ${p * a} × ${c} = ${p * a * c}`); } },
      { t: 3, f: () => { const x = rnd(3, 9), y = rnd(11, 20), z = rnd(2, 5);
        const [ex, name] = pick([[`${x} + ${y} = ${y} + ${x}`, 'Değişme'], [`(${x} × ${z}) × 10 = ${x} × (${z} × 10)`, 'Birleşme'], [`${x} × (10 + ${z}) = ${x} × 10 + ${x} × ${z}`, 'Dağılma']]);
        return q(`"${ex}" hangi özellik?`, name, ['Değişme', 'Birleşme', 'Dağılma', 'Eşitlik bozulur'].filter(n => n !== name), `${ex} → ${name} özelliği`); } },
    ]
  },
  {
    title: 'İşlem önceliği', tiered: true,
    kaz: 'MAT.5.2.2 · Doğal sayılarla dört işlemde işlem önceliğini yorumlar ve uygular.',
    text: 'Önce parantez, sonra kare ve küp, sonra çarpma ve bölme, en son toplama ve çıkarma.',
    gen: [
      { t: 1, f: () => { const n = rnd(2, 5);
        return q(`${n}² = ?`, n * n, [n * 2 === n * n ? n * n + 1 : n * 2, n + 2 === n * n ? n * n + 2 : n + 2, n * n + n], `${n}² = ${n} × ${n} = ${n * n}`); } },
      { t: 1, f: () => { const a = rnd(1, 9), b = rnd(2, 5), c = rnd(2, 4);
        return q(`${a} + ${b} × ${c} = ?`, a + b * c, [(a + b) * c, a + b + c, a * b + c], `Önce çarpma: ${b} × ${c} = ${b * c}, sonra ${a} + ${b * c} = ${a + b * c}`); } },
      { t: 2, f: () => { const a = rnd(2, 6), b = rnd(2, 6), c = rnd(2, 4);
        return q(`(${a} + ${b}) × ${c} = ?`, (a + b) * c, [a + b * c, a + b + c, a * c + b], `Önce parantez: ${a} + ${b} = ${a + b}, sonra × ${c} = ${(a + b) * c}`); } },
      { t: 2, f: () => { const c = rnd(2, 4), b = c * rnd(2, 5), a = b / c + rnd(3, 12);
        return q(`${a} − ${b} ÷ ${c} = ?`, a - b / c, [a + b / c, b / c, a + c], `Önce bölme: ${b} ÷ ${c} = ${b / c}, sonra ${a} − ${b / c} = ${a - b / c}`); } },
      { t: 2, f: () => { const n = rnd(2, 4);
        return q(`${n}³ = ?`, n ** 3, [n * 3, n * n, n ** 3 + n], `${n}³ = ${n} × ${n} × ${n} = ${n ** 3}`); } },
      { t: 3, f: () => { const n = rnd(2, 4), b = rnd(2, 4), c = rnd(2, 4);
        return q(`${n}² + ${b} × ${c} = ?`, n * n + b * c, [(n * n + b) * c, n * n + b + c, n * 2 + b * c === n * n + b * c ? n * n + b * c + 2 : n * 2 + b * c], `Önce kare: ${n * n}, sonra çarpma: ${b * c}, en son toplama: ${n * n + b * c}`); } },
      { t: 3, f: () => { const p = rnd(2, 4), s = pick([6, 8, 10]), t = rnd(2, 5);
        return q(`${p} paket ${s}'${({ 6: 'lı', 8: 'li', 10: 'lu' })[s]} kalem ve ${t} tane tek kalem alındı. Hangi işlem toplam kalemi verir?`, `${p} × ${s} + ${t}`, [`${p} × (${s} + ${t})`, `${p} + ${s} × ${t}`, `${p} + ${s} + ${t}`], `Önce paketlerdeki kalemler (${p} × ${s}), sonra tek kalemler: ${p} × ${s} + ${t} = ${p * s + t}`); } },
    ]
  },
  {
    title: 'Örüntüler', tiered: true,
    kaz: 'MAT.5.2.3 · Sayı ve şekil örüntülerinin kuralına ilişkin muhakeme yapar.',
    text: 'Örüntünün her adımda kaç arttığını bul. Sonra adım sayısıyla terim arasındaki kuralı yakala.',
    gen: [
      { t: 1, f: () => { const d = rnd(2, 5), a = rnd(1, 6); const t = [0, 1, 2, 3].map(i => a + i * d);
        return q(`${t.join(', ')}, ?  Sonraki sayı kaç?`, a + 4 * d, [a + 4 * d + 1, a + 5 * d, a + 3 * d + 1], `Her adımda ${d} artıyor: ${t[3]} + ${d} = ${a + 4 * d}`); } },
      { t: 1, f: () => { const k = rnd(2, 5), n = rnd(3, 5);
        return q(`Kumbaraya her gün ${k} TL atılıyor. ${n} gün sonra kumbarada kaç TL olur?`, k * n, [k + n, k * (n - 1), k * n + k], `Her gün ${k} TL: ${k} × ${n} = ${k * n} TL`); } },
      { t: 2, f: () => { const d = rnd(2, 5); const t = [1, 2, 3, 4].map(i => d * i);
        return q(`${t.join(', ')}, …  Bu örüntünün 10. adımı kaç?`, d * 10, [d * 10 + d, d + 10, d * 9], `Kural: adım sayısının ${d} katı → ${d} × 10 = ${d * 10}`); } },
      { t: 2, f: () => { const n = rnd(4, 7);
        return q(`1. şekil 3 kibrit, 2. şekil 5 kibrit, 3. şekil 7 kibrit. ${n}. şekil kaç kibrit?`, 2 * n + 1, [2 * n, 3 * n, 2 * n + 3], `Her şekilde 2 kibrit artıyor. Kural: adımın 2 katının 1 fazlası → 2 × ${n} + 1 = ${2 * n + 1}`); } },
      { t: 3, f: () => { const d = rnd(2, 4); let c = rnd(1, 3); if (c === d) c = 1; const t = [1, 2, 3, 4].map(i => d * i + c);
        return q(`${t.join(', ')}, …  Bu örüntünün kuralı hangisi?`, `Adımın ${d} katının ${c} fazlası`, [`Adımın ${d} katı`, `Adımın ${c} katının ${d} fazlası`, `Adımın ${d + c} katı`], `1. adım: ${d} × 1 + ${c} = ${t[0]}, 2. adım: ${d} × 2 + ${c} = ${t[1]} ✓`); } },
      { t: 3, f: () => { const d = rnd(2, 4), c = rnd(1, 3); const t = [1, 2, 3, 4].map(i => d * i + c);
        return q(`${t.join(', ')}, …  Kural: adımın ${d} katının ${c} fazlası. 10. adım kaç?`, d * 10 + c, [d * 10, d * 10 + c + d, (d + c) * 10], `${d} × 10 + ${c} = ${d * 10 + c}`); } },
    ]
  },
  {
    title: 'Algoritmalar', tiered: true,
    kaz: 'MAT.5.2.4 · Temel aritmetik işlem içeren algoritmaları yorumlar.',
    text: 'Algoritma, sırayla yapılan adımlardır. Adımları atlamadan uygula.',
    gen: [
      { t: 1, f: () => { const x = rnd(2, 9), k = rnd(2, 4);
        return q(`Başla → ${x} gir → ${k} ile çarp → Yazdır. Ekranda ne yazar?`, x * k, [x + k, x * k + k, x], `${x} × ${k} = ${x * k}`); } },
      { t: 1, f: () => { const s = rnd(1, 5), k = rnd(2, 3);
        return q(`Sayı ${s}. "${k} ekle" adımını 2 kez yap. Sonuç kaç?`, s + 2 * k, [s + k, s + 3 * k, s * 2 + k === s + 2 * k ? s + 2 * k + 1 : s * 2 + k], `${s} + ${k} = ${s + k}, + ${k} = ${s + 2 * k}`); } },
      { t: 2, f: () => { const x = rnd(2, 6), k = rnd(2, 3), m = rnd(1, 5);
        return q(`Başla → ${x} gir → ${k} ile çarp → ${m} ekle → Yazdır. Ekranda ne yazar?`, x * k + m, [(x + m) * k, x + k + m, x * k + m + k], `${x} × ${k} = ${x * k}, + ${m} = ${x * k + m}`); } },
      { t: 2, f: () => { const d = rnd(2, 5), n = rnd(2, 5);
        return q(`${d * n} sayısından 0 olana kadar ${d} çıkarılıyor. Kaç kez çıkarılır?`, n, [n + 1, d === n ? n + 3 : d, n + 2], `Tekrar tekrar çıkarma bölmedir: ${d * n} ÷ ${d} = ${n}`); } },
      { t: 2, f: () => { const x = rnd(2, 9);
        return q(`Sayı 5'ten büyükse 2 ile çarp, değilse 10 ekle. Sayı ${x} ise sonuç?`, x > 5 ? x * 2 : x + 10, [x > 5 ? x + 10 : x * 2, x, x + 2], x > 5 ? `${x}, 5'ten büyük: ${x} × 2 = ${x * 2}` : `${x}, 5'ten büyük değil: ${x} + 10 = ${x + 10}`); } },
      { t: 3, f: () => { const x = rnd(12, 20), k = rnd(2, 6), m = 2, y = x - k;
        return q(`Başla → ${x} gir → ${k} çıkar → ${m} ile çarp → Yazdır. Ekranda ne yazar?`, y * m, [x * m - k, y + m, x * m], `${x} − ${k} = ${y}, × ${m} = ${y * m}`); } },
      { t: 3, f: () => { const p = pick([2, 3, 4, 5]);
        return q(`700 g'lık paket ${7 * p} TL. Önce 7'ye böl (100 g fiyatı), sonra 10 ile çarp. 1 kg kaç TL?`, 10 * p, [7 * p, 10 * p + 7, p], `${7 * p} ÷ 7 = ${p} TL (100 g), ${p} × 10 = ${10 * p} TL (1 kg)`); } },
    ]
  }
];
