# 04 — Backplane ve Mekanik

> Bu dokümandaki kararlar **geriye dönük değiştirilemez**. Üretilmiş her node
> buraya bağlıdır.

---

![Blade şasi üstten kesit](img/02-blade-kizak-kesit.svg)

## 1. Mekanik mimari: blade mi, kutu-içinde-kutu mu?

İki paradigma var ve bu seçim node maliyetinden termal tasarıma kadar her şeyi
belirliyor.

| | **(A) Kutu-içinde-kutu** | **(B) Gerçek blade** |
|---|---|---|
| Node | Kendi plastik muhafazası olan kapalı modül | **Çıplak PCB + ön panel**, kızağa sürülür |
| Benzer | Beckhoff / Wago DIN klemens modülleri | Blade server, VME / cPCI subrack |
| Node başı muhafaza maliyeti | $2–5 | **$0** |
| Isı yolu | PCB → hava → plastik → hava → şasi | **PCB → doğrudan hava kanalı** |
| Mekanik hizalama | Kutu toleransı + host toleransı | **Kızak, PCB kenarını boydan boya tutuyor** |
| Titreşim davranışı | PCB kutu içinde serbest, rezonans riski | **PCB iki kenarından 110 mm boyunca destekli** |
| EMI | Plastik ekranlamaz | **Metal şasi ekran** |
| Çıplak PCB teması | Yok | Servis sırasında var — ele alınmalı |

### Karar: (B) gerçek blade · D-60

Dört bağımsız gerekçe, hepsi karavan bağlamında ağır basıyor:

**1. Termal — belirleyici olan bu.**
[11 §6](11-cikis-node-topolojileri.md#6-iletim-kaybı-ve-termal)'da paketlenmiş
node'da doğal konveksiyonun yetmediğini hesaplamıştık. Kutu-içinde-kutu bunu
daha da kötüleştiriyor: plastik ısı iletkenliği ~0.2 W/mK, yani her node'un
etrafında bir yalıtım katmanı var. Blade'de PCB doğrudan zorlanmış hava
akışında.

**2. Node maliyeti — sekiz kez ödenen kalem.**
Muhafaza başına $2–5, 8 node'da $16–40. K1'in
([01 §3](01-sistem-genel-bakis.md#3-tasarımı-yöneten-kısıtlar)) tam olarak
kaçınmamızı söylediği türden bir maliyet.

**3. Titreşim (K5) — blade daha iyi.**
Sezgiye aykırı ama doğru: kızak, PCB'yi üst ve alt kenarından **110 mm boyunca
sürekli** destekliyor. Kutu içinde 4 vidayla tutulan bir PCB'nin rezonans
frekansı çok daha düşük. Karavan yol titreşiminde bu gerçek bir fark.

**4. Hizalama — kart kenarı konnektörünün ihtiyacı olan şey.**
Kızak, konnektöre giriş açısını ve yüksekliğini garantiliyor. Kutu-içinde-kutuda
iki tolerans zinciri üst üste biniyor.

### 1.1 Blade'in bedeli ve karşılığı

| Sorun | Çözüm |
|-------|-------|
| Servis sırasında çıplak PCB'ye temas (ESD) | Ön panel tutamak görevi görüyor; node'lar ESD poşetinde sevk edilir; ön panelde "PCB'ye dokunmayın" işareti |
| **AC node şebeke** | **Kablo:** IP20 pluggable (D-38). **PCB:** 230 V adasına klipsli bariyer — tam kutu değil · 🟢 D-64 |
| Toz / nem | Şasi sorumluluğu — ön panel dizisi kapalı yüzey oluşturur, boş slotlara kör kapak |
| Klemens kuvvetleri PCB'ye biniyor | Ön panel PCB'ye köşebent + 2 vida ile rijit bağlanır; kuvvet panelden şasiye aktarılır |

**D-64 · 🟢** AC kablo IP20 fişte (D-38). Node içi: yalnız 230 V adasına
**klipsli plastik bariyer** (röle pimi, iz). Tam kutu yok — blade termali durur.

---

## 2. Slot ve node ölçüleri

Çalışma draftı Rev 0.1'den alınan gerçek ölçüler
([12 §1](12-mekanik-referans-rev01.md#1-drafttan-alınan-somut-veriler)) · D-58

| | 1U | 2U |
|---|-----|-----|
| **Slot adımı** | **17.5 mm** | **35.0 mm** |
| Ön panel | 17.5 × ~80 mm | 35.0 × ~80 mm |
| PCB (yükseklik × derinlik) | ~75 × 110 mm | ~75 × 110 mm |
| PCB kalınlığı | 1.6 mm | 1.6 mm |

```
Node slotları   =  8 × 17.5  =  140 mm
Host slotu (2U) =              35 mm     ← node kapasitesi tüketmez
                               ───────
Toplam slot alanı            = 175 mm    (+ duvarlar ≈ 185 mm)
```

**Host da bir blade** — node'larla aynı kızak, ön panel ve kapalı vida
sistemini kullanır, kendi özel slotunda durur. Gerekçe ve alan hesabı:
[02 §7](02-host-mimarisi.md#7-hostun-mekanik-formu) · D-66

> ⚠️ **Host konnektörü node konnektöründen farklıdır** (slot başına
> RST#/PRESENT# hatları host'a gider). **Mekanik keying zorunlu** — node host
> slotuna, host node slotuna takılamamalı.

**17.5 mm neden doğru:** Modüler şalt cihazlarının (sigorta, kontaktör) tek
kutup genişliği 17.5/18 mm — yani DIN ekosistem argümanı geçerli. Ve 22.5 mm'ye
göre cihazı **40 mm daraltıyor**; karavanda hacim pahalı.

![1U node anatomisi](img/03-node-1u-anatomi.svg)

### 2.1 Bileşen yüksekliği · D-61

```
Slot adımı                  17.5 mm
PCB kalınlığı              − 1.6 mm
Komşuya emniyet açıklığı   − 1.5 mm
                            ───────
1U bileşen tavanı            14.4 mm   (tek yüzde)
```

**Kural: 1U dene; sığmazsa 2U.** Kanal kesilmez, egzotik alçak profil dayatılmaz.
2U baskı değil — yer var (D-75 tavanı 2U). 4U yok.

DC-L-16A-4 hedef 1U; latching >14.4 mm (pratikte ≤12 mm gövde payı) → aynı 4
kanal 2U. COM magjack, host izole DC-DC: aynı kural.

MOSFET DO zaten alçak. Bobin gerilimi kısıt değil (5 V latching standart).

---

## 3. Şasi ve kızak sistemi

### 3.1 Kızak — 16 parça değil, 2 parça

```
        ┌──────────────────────────────────────────┐
        │  ÜST KIZAK RAYI (tek parça, 8 oluk)      │
        ├──┬──┬──┬──┬──┬──┬──┬──┬──────────────────┤
        │  │  │  │  │  │  │  │  │                  │
   PCB →│  │  │  │  │  │  │  │  │  ← 17.5 mm adım  │
        │  │  │  │  │  │  │  │  │                  │
        ├──┴──┴──┴──┴──┴──┴──┴──┴──────────────────┤
        │  ALT KIZAK RAYI (tek parça, 8 oluk)      │
        └──────────────────────────────────────────┘
                          ↓
              arka: backplane PCB + kart kenarı soketleri
```

Slot başına iki ayrı kızak parçası (16 adet) yerine **üstte ve altta birer
kalıplı/ekstrüzyon ray.** Sonuç:

- 2 parça, 16 değil → montaj ve maliyet
- Oluklar aynı parçada olduğu için **adım toleransı kalıptan geliyor**, montajdan değil
- Backplane konnektör dizisiyle hizalama tek referansa bağlı

Prototipte 3D baskı, seri üretimde enjeksiyon kalıp veya alüminyum ekstrüzyon.

**İlk kasa tam zarftır · D-70:** 8U node alanı + sabit 2U host yuvası.
2–3 slotluk ara gövde yok — ikinci kalıp/baskı maliyeti tam zarftan pahalı.
Aynı 3D model hem prototip hem hedef üründür.

### 3.2 Şasi malzemesi · D-62

| Aşama | Yapı |
|-------|------|
| Prototip | **3D baskı gövde + Al kızak** (D-70 tam zarf) |
| Seri | **Alüminyum ekstrüzyon gövde** + sac ön/arka panel |

Al ekstrüzyon: titreşim (K5), EMI, **ısı yolu** — kızak ısıyı gövdeye verir.
Seride 3D yok.

### 3.3 Takma / çıkarma · 🟢 D-45

```
Kart kenarı sürtünme kuvveti  ≈  12 pin × ~0.5 N  ≈  6 N
```

Parmakla oturur. Tutma: ön panelde **kapalı (captive) vida** — 1U'da 1, 2U'da
2. Karavanda düşmeyen vida; mandal yok.

**Hot-plug (D-24) durur.** Vida elektrik değil: sök → çek → tak → sık. PRESENT#,
load switch, discovery aynı. Fretting'e mandaldan daha iyi (K5).

Kızak kenarları tutar; vida öne-arkaya yürümeyi keser. Yalancı dil (D-16) sağ
arkayı yatar — vidanın yerine geçmez.

### 3.4 Boş slotlar · D-63

Boş slotlara **kör kapak zorunlu** (pasif baca, D-57):
- Hava kısa devre olmasın
- Toz
- Ön yüz

Opsiyonel değil. Kapak da kapalı vida (D-45) ile.

---

## 4. Konnektör seçimi

| Seçenek | Node tarafı maliyet | Servis ömrü | Stagger |
|---------|---------------------|-------------|---------|
| **PCB kart kenarı (gold finger)** | **$0 — sadece PCB** | ENIG ~50 takma · sert altın 500+ | **Bedava** (finger boyu ile) |
| Pin header 2×N | ~$0.15 | Düşük | Yok |
| DIN 41612 | ~$2–4 | Çok yüksek | Var |

### Karar: PCB kart kenarı, 2.54 mm adım, 2 × 6 = **12 pin** · D-32

> ⛔ İlk karar D-14 (26 pin) **D-32 tarafından supersede edildi.** Kart kenarı /
> gold finger tercihi aynen korundu; değişen yalnızca pin sayısı. Gerekçeler:
> [§5.3](#53-neden-26-değil-12--tarihsel-karşılaştırma)

Blade mimarisi bu kararı **güçlendiriyor**: kızak sistemi, kart kenarı
konnektörünün en hassas olduğu şeyi — giriş açısı ve yükseklik hizalaması —
garanti altına alıyor. Kutu-içinde-kutuda bu iki tolerans zincirine bağlıydı.

**Üretim notu:** JLCPCB gold finger opsiyonu ek kurulum ücreti gerektiriyor.
Prototipte ENIG yeterli (~50 takma çevrimi); seri üretimde sert altına geçilir.
Bu bir PCB süreç kararı, tasarımı etkilemiyor.

---

## 5. Pinout

![Kart kenarı stagger ve pin dizilimi](img/04-kartkenari-stagger.svg)

### Karar: 12 pin, 2 × 6, 4 kademeli mate sırası · D-32

> **26 pin → 12 pin.** İlk taslak uçtan uca sorgulandı ve yarıdan fazlası
> gereksiz çıktı. Gerekçeler §5.3'te tek tek.

| # | Sinyal | Yön | Mate | Açıklama |
|---|--------|-----|------|----------|
| 1 | **GND** | — | **1** | Referans, en uzun finger |
| 2 | **GND** | — | **1** | Redundans — titreşimde tek kontak kesintisi node'u düşürmemeli (K5) |
| 3 | **+5V** | → node | 2 | Tek ray. 1U 250 mA sürekli (D-29); darbe ≤800 mA |
| 4 | **+5V** | → node | 2 | Redundans |
| 5 | **BUS_A** | çift yön | 3 | RS-485 non-inverting |
| 6 | **BUS_B** | çift yön | 3 | RS-485 inverting |
| 7 | **MOD_RST#** | host → node | 3 | Slot başına. Node'da 10k pull-**down** |
| 8 | *RSVD1* | — | 3 | Rezerve |
| 9 | *RSVD2* | — | 3 | Rezerve |
| 10 | *RSVD3* | — | 3 | Rezerve |
| 11 | *RSVD4* | — | 3 | Rezerve |
| 12 | **PRESENT#** | node → host | **4 (en kısa)** | GND'ye bağlı, son oturan pin |

**8 fonksiyonel + 4 rezerve.** Rezerve sayısı keyfi değil: bir diferansiyel çift
(2) + iki tek uçlu sinyal (2) = gelecekte "bunu atlamışız" denebilecek
senaryoların pratikte tamamını karşılıyor.

### 5.1 Mate sırası

```
Kademe 1 (en uzun)   GND ×2       → referans kurulur
Kademe 2             +5V ×2       → besleme gelir
Kademe 3             Bus, RST#, rezerve
Kademe 4 (en kısa)   PRESENT#     → "tam oturdu"
```

**PRESENT#'in en son oturması tasarımın kilit taşı.** Host, PRESENT# düşene
kadar node'u yok sayar; yarım oturmuş bir node sistemi hiç etkilemez.

### 5.2 Konnektör ölçüsü

```
12 pin, 2 sıra × 6, 2.54 mm adım  →  kenar uzunluğu 15.24 mm
```

*(Karşılaştırma için: supersede edilen 26 pinli tasarım 2 × 13 → 33.0 mm idi.)*

75 mm'lik kart kenarında rahat yer var. Hizalamayı zaten kızak yapıyor (§4),
konnektörün uzun olmasına gerek yok.

### 5.3 Neden 26 değil 12 — tarihsel karşılaştırma

> 📎 Bu bölüm **tarihseldir.** İlk taslaktaki 26 pinli pinout'un (D-14) neden
> 12 pine indirildiğini kayıt altında tutar. Güncel bağlayıcı pinout §5'teki
> tablodur (D-32).

#### GND ×4 → ×2

```
1U sürekli tavan            250 mA
Bobin darbesi (tepe)        ≤ 800 mA @5 V
Tek 2.54 mm gold finger     1–3 A
```

Akım açısından **tek pin bile fazlasıyla yeterli.** İkinci pin akım için değil,
**titreşim altında kontak redundansı** için (K5) — aralıklı tek bir kontak
rastgele reset'lere yol açar. Üçüncü ve dördüncü pinin hiçbir gerekçesi yoktu.

#### VBUS_RAW (12–48 V) → kaldırıldı, tek +5V rayı

Soru: backplane'den 5 V'tan yüksek gerilime gerçekten ihtiyacı olan bir node
var mı?

| Aday ihtiyaç | Gerçek durum |
|--------------|--------------|
| Latching röle bobini | **5 V bobinli latching röleler standart katalog ürünü** |
| Dijital giriş 24 V | Saha klemensinden gelir, backplane'den değil |
| İzole DC-DC primer | 5 V'tan sorunsuz çalışır |
| MOSFET high-side gate | Zaten charge pump gerektiriyor |
| **Analog çıkış 0–10 V compliance** | **Tek gerçek ihtiyaç** — lokal boost gerekiyor (~$0.30) |

Yani 12–48 V dağıtımının tek gerekçesi, henüz tasarlanmamış tek bir node
tipiydi. O node'a ~$0.30'luk bir boost koymak, **sekiz slota iki pin + backplane
boyunca yüksek gerilim dağıtmaktan** ucuz ve güvenli.

Gerilim düşümü kontrolü:

```
En uzak slota backplane izi ≈ 150 mm, 0.5 mm genişlik 1oz  ≈ 150 mΩ
250 mA sürekli düşüm = 38 mV
800 mA darbe düşüm   = 120 mV     → kabul
Node havuzu 1.6 A, host yakınında geniş döküm
```

> **Bobin gerilimi serbest.** 5 V doğrudan veya 12/24 V + lokal boost. 5 V
> varyantı aranmak zorunda değil — 5 V tarafı akım tavanı 800 mA (D-29/D-68).

#### ADDR0–3 → kaldırıldı, host adres atıyor

Soru: node fiziksel konumunu bilmek zorunda mı?

**Hayır.** Host'ta zaten **slot başına MOD_RST#** var — bu, çakışmasız
enumerasyon için yeterli seçici mekanizma:

```
1. Host tüm node'ları reset'te tutar
2. Sadece slot N'in RST#'ini bırakır  →  bus'ta tek node uyanık
3. Adressiz node ile konuşur, UID'sini okur, kısa adres atar
4. Sırayla tekrarlar
```

Çakışma imkânsız, çünkü aynı anda yalnızca bir node uyanık.

| | Coğrafi (ADDR pinleri) | Host atamalı |
|---|---|---|
| Pin maliyeti | **4 pin × 8 slot** | 0 |
| Node firmware'i | Pin okumalı | **Konum kavramı hiç yok** |
| Açılış süresi | Anında | ~400 ms (8 × ~50 ms) |
| Reset sonrası | Otomatik | Host yeniden atamalı |

Node'un konumdan tamamen habersiz olması aslında **daha temiz**: aynı firmware,
aynı davranış, nereye takılırsa takılsın. Host zaten hangi slotta ne olduğunu
biliyor — bilmesi gereken taraf o.

#### SYNC → kaldırıldı, broadcast çerçeve

SYNC'in işi tüm node'ların aynı anda I/O latch'lemesiydi. Ama **bus zaten
broadcast** — bir "şimdi uygula" çerçevesi tüm node'lara aynı anda ulaşıyor.

```
Donanım strobe eşzamanlılığı   ~ns
Broadcast çerçeve              ~µs   (çerçeve alım jitter'ı)
Karavan yüklerinin ihtiyacı    ~ms
```

µs ile ns arasındaki fark bu uygulamada ölçülemez. **1 pin yerine 1 fonksiyon
kodu.**

#### FAULT# → kaldırıldı, poll ile

FAULT#'un kazancı, arıza bildirimini poll gecikmesinden kurtarmaktı: 10 Hz'de
en fazla **100 ms**.

Ama **gerçek zamanlı koruma zaten node'un işi** — kısa devre için 100 ms de
çok geç, node kendi kanalını µs'ler içinde kapatmak zorunda. Host'un öğrenmesi
kayıt ve uyarı içindir; 100 ms fark etmez.

**Ek kazanç:** Wired-OR hattın bir arıza modu vardı — hattı düşük tutan tek
arızalı node, diğer tüm node'ların arızasını maskeliyordu. O mod da ortadan
kalktı.

> Node arızayı **latch'lemeli**, böylece iki poll arasında oluşan olay kaybolmaz.

#### BOOT# → kaldırıldı, bootloader penceresi

BOOT#'un işi, uygulaması kilitlenmiş bir node'u kurtarmaktı. Ama per-slot RST#
varken daha basit bir yol var:

```
1. Host o slotun RST#'ini çeker  →  uygulama durur
2. RST# bırakılır                →  bootloader çalışıyor, uygulama henüz değil
3. Bootloader ~30 ms bus'ı dinler
4. Host "bootloader'da kal" çerçevesi gönderir
```

Kilitlenmiş uygulama bu pencerede **çalışmıyor**, dolayısıyla engel olamaz.
Bus'ı meşgul eden başka bir node varsa host onu da reset'te tutabilir.

Bedeli: her açılışta ~30 ms gecikme. Açılışlar nadir.

#### Rezerve pinler 6 → 4

| Kaldırılan | Gerekçe |
|------------|---------|
| Tam dupleks çifti (2 pin) | Yarım dupleks 500 kbaud'da 40× tarama marjı var ([05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi)). Tam dupleks senaryosu gerçekçi değil |
| 3.3 V rezervesi (1 pin) | 3.3 V dağıtmamaya zaten karar verilmişti ([12 §3.3](12-mekanik-referans-rev01.md#33-backplane-rail-sayısı-33v-tartışmalı)) — kullanmamaya karar verdiğimiz şey için pin ayırmak tutarsızdı |
| Genel yedek 3 → 4 | Net olarak arttı: 4 rezerve = 1 diferansiyel çift + 2 tek uçlu |

**BUS_A/B çifti hâlâ CAN'e uygun** — ileride gerekirse sadece transceiver
değişir.

### 5.4 Sadeleşmenin ikinci kazancı: backplane

```
26 pin × 8 slot  =  208 net
12 pin × 8 slot  =   96 net
```

Backplane'de yönlendirilecek net sayısı **yarıdan fazla azaldı.** Bu, backplane
PCB'sini büyük olasılıkla **2 katmanda** tutulabilir hale getiriyor — ayrı bir
maliyet ve tedarik kazancı.

Konnektör maliyeti de düşüyor: 12 pinli kart kenarı soketi ~$0.30, 26 pinli
~$0.60 → 8 slotta ~$2.40 tasarruf.

## 6. Hava akışı ve termal

Blade mimarisinin asıl kazandığı yer. **Soğutma pasif · D-57** — üründe fan yok.

![Hava akışı](img/05-hava-akisi.svg)

### 6.1 Akış düzeni — baca

```
   ön panel                                      arka / üst
   (giriş)                                       (çıkış)
      │                                             │
      ▼                                             ▼
   ┌──┬─────────────────────────────────────────┬───┐
   │  │  ░░ blade ░░  ← 15 mm kanal →           │   │  ızgara
   │  │  ░░ blade ░░                            │   │
   │  │  ░░ blade ░░     Al kızak = ısı yolu    │   │
   └──┴─────────────────────────────────────────┴───┘
```

Her blade çifti arasında ~15 mm kanal (17.5 mm adım − 1.6 mm PCB − bileşen
yüksekliği). Hava ön panel deliklerinden girer, blade yüzeyini yalar, arkadan
veya üstten çıkar — **baca**, fan değil.

**Asıl ısı yolu konveksiyon değil iletimdir:** Al kızak rayı PCB kenarına
dayanır, ısıyı şasiye taşır. Seri üretimde Al ekstrüzyon gövde (D-62) bu
yolu büyütür. 3D baskı prototipte de **kızak alüminyum kalır** (D-70).

**Boş slotlara kör kapak zorunlu** (§3.4) — baca kısa devre olmasın.

### 6.2 Neden fan yok

Fan gürültü, toz, arıza tek noktası ve enerji. Karavan cihazında sürekli
sorun. Bu yüzden soğutma **tasarım kısıtı**, ek donanım değil.

Paketlenmiş 1U'da yalnız havaya bakan yüzey yetmez
([11 §6](11-cikis-node-topolojileri.md#6-iletim-kaybı-ve-termal)). Cevap fan
değil:

| Yol | Rol |
|-----|-----|
| Al kızak + şasi | İletim — birincil |
| Ön panel metal | Yüksek akımlı node'da ısı yayıcı (D-54) |
| Baca + kör kapak | Zayıf konveksiyon, toz |
| Node dissipasyon tavanı | Spec'e yazılır; sığmayan node 2U olur veya kanal sayısı düşer |

**Sonuç:** yüksek akımlı node'un termali, node spec işinin parçası. Fan geri
gelmez; sığmazsa node değişir.

---

## 7. 2U node stratejisi

| Seçenek | Değerlendirme |
|---------|---------------|
| **(a) Sol = elektrik, sağ = yalancı dil** | Tek presence, tek RST#, tek load switch. Sağ konnektör yalnız mekanik |
| (b) Her iki konnektöre de elektriksel oturur | 2× güç; canlı takmada yarım mate + iki PRESENT# |

### Karar: (a) + bakırsız sağ dil · 🟢 D-16

2U = **tek PCB, 35 mm**, iki kızak oluğu. Elektrik yalnız **sol** gold finger
(12 pin). Sağda aynı zarfta **yalancı dil** — sağ slot konnektörüne oturur,
yalnız mekanik destek (K5 titreşim, 2U'nun sola yaslanması).

```
        slot N (sol)              slot N+1 (sağ)
     ┌──────────────┐          ┌──────────────┐
     │ 12 pin ENIG  │          │ bakırsız FR4 │
     │ GND…PRESENT# │          │   yalancı    │
     └──────┬───────┘          └──────┬───────┘
            │ elektriksel             │ mekanik, net yok
```

**Neden bakırsız:** sağ konnektör canlı (+5V, bus, RST#, PRESENT#). Dil üzerinde
bakır — hele döküm — pinleri kısa devre eder. PRESENT# pad'i olsa host N+1'de
sahte 1U görür. Dil: PCB kalınlığı (1.6 mm), pah, bakır/soldermask yok; yaylar
FR4'e basar.

İsteğe bağlı: dil **biraz daha uzun** lead-in — önce mekanik oturur, sonra sol
elektrik. PRESENT# yine en kısa, sol tarafta.

Güç: 2U tavanı 300 mA, sol konnektörün 2 × +5V kontağından. Kontak kapasitesinin
çok altında. Çift elektrik gerekmez.

### 7.1 Adresleme tutarlılığı

```
Slot 3–4'e takılı bir 2U node:
  · Elektrik yalnız slot 3
  · Slot 4'te yalancı dil — PRESENT# yüksek kalır (bakır yok)
  · Host slot 3 RST#'ini bırakınca uyanır, adres = 3
  · Descriptor form_factor = 2U
  · Host slot 4'ü "2U kapalı" işaretler
```

Host atamalı adresleme 2U'yu kendiliğinden çözüyor. Yalancı dil ön vidanın
(D-45) yerine geçmez — arkada ikinci yatak.

---

## 8. Hot-plug değerlendirmesi

| Gereksinim | Maliyet | Not |
|------------|---------|-----|
| Staggered kontak | **$0** | Kart kenarı finger boyları ile (§4) |
| Slot başına akım sınırlı load switch | ~$0.20 | Zaten arıza izolasyonu ve S3 için gerekli ([06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması)) |
| Node tarafı soft-start | ~$0.15 | |
| Hot-plug toleranslı RS-485 transceiver | **$0** | Aynı fiyat sınıfında mevcut |
| Protokol desteği | **$0** | Timeout tabanlı; kaybolan node = timeout, yeni node = PCA9555 INT# |
| **Toplam ek** | **~$0.35 / node** | |

### Karar: v1 hot-plug **desteklenir** · 🟢 D-24

Canlı tak-çıkar birinci sınıf. "v2'de ekleriz" yok — pinout, load switch,
PRESENT# INT, discovery ve bütçe kontrolü şimdi. Sonradan 1U dolmaz / enerji
yetmez / yazılım baştan yazılmaz.

Donanım bedeli zaten S3 ve arıza izolasyonu (~$0.35/node). Ek iddia: host
firmware INSERT/REMOVE'u tarama döngüsünde işler; ENABLE öncesi güç bütçesi.

### 8.1 v1'de zorunlu

- Staggered finger (PRESENT# en kısa)
- Slot load switch + node soft-start
- Glitch-free RS-485 transceiver
- PCA9555 INT# → canlı discovery (D-18, D-34)
- RST# varsayılan pull-down (D-22)

### 8.2 Doğrulama (iddiayı düşürmez, testi erteler)

- ≥50 tak-çıkar çevrimi
- Komşu rail dip
- Takma sırasında bus trafiği

Sonradan eklemenin bedeli tüm pinout + node ailesi — o yüzden iddia v1'de.
