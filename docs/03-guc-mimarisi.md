# 03 — Güç Mimarisi

## 1. Giriş koruma katı

### 1.1 Gerilim sınıfı zinciri

48V nominal endüstriyel besleme, ±%10 toleransla:

```
Nominal maksimum          48 V × 1.10  =  52.8 V  (sürekli)
TVS standoff seçimi                       58   V  (> 52.8 V olmalı)
TVS clamp gerilimi @ Ipp                  ~93  V  (SMBJ58A sınıfı)
                                          ─────
Downstream parçaların görebileceği en yüksek gerilim
```

Bu zincir, ön kattaki her parçanın gerilim sınıfını belirliyor. Ve burada
maliyeti belirleyen bir çatal var.

### 1.2 Kritik çatal: 100 V mu, kesip 60 V mu?

| Yaklaşım | Sonuç |
|----------|-------|
| **(a)** Tüm ön kat 100 V | Buck 100 V/3 A — LCSC az, pahalı. OV'de FET açmaz, her parça 100 V |
| **(b)** High-side kesme + TVS | OV'de FET **açar (keser)** → downstream **60 V**. TVS enerjiyi yutar |

### Karar: (b) koruma kontrolcüsü + high-side N-FET · 🟢 D-09

Karavan/tekne: **şasi negatif, high-side anahtar.** GND dönüşüne FET yok —
şasi sürekliliği güvenlik.

**VIN galvanik izole değil.** İzolasyon saha portunda (D-07). Bataryayı
izole DC-DC ile kesmek backplane'i şasiden koparır; kaçak ve SELV referansı
bozulur. Güvenlik = high-side kesme + sağlam GND, izolasyon değil.

A (P-FET + gate zener) ile B aynı iş: high-side, GND bütün, 60 V sonrası.
B daha **stabil ve güvenli**:

| | P-FET + zener | Kontrolcü + N-FET |
|--|----------------|-------------------|
| Ters polarite | Ayrık, SOA el kitabı | Otomotiv kontrolcüsü, karakterize |
| OV | Zener hilesi, gate ±20 V | UV/OV pini, FET'i kapatır |
| Inrush | Gate RC | Kontrollü |
| Isı @ ~1 A (12 V) | 100 V P-FET R_DS yüksek | 60–80 V N-FET bol, düşük R_DS |
| Bedel | FET pahalı | Kontrolcü ~+$1, FET ucuz |

**Topoloji:** ideal-diyot / koruma kontrolcüsü (LM7480 / LTC4368 sınıfı, aday)
+ high-side N-FET. Ters + OV için parçanın gerektirdiği **back-to-back** FET.
SKU şemada LCSC.

TVS hâlâ var — kontrolcü keser, TVS darbeyi yer.

### 1.3 Zincir

```
Klemens → Sigorta (2.5A yavaş) → CM choke → TVS 58V → kontrolcü + high-side N-FET
        → Bulk kapasitör → Ana buck
```

| Kademe | Amaç | Aday parça sınıfı |
|--------|------|-------------------|
| Sigorta | Kalıcı arıza izolasyonu | 2.5A yavaş atan, 125V DC kesme |
| CM choke | İletilen emisyon + EFT | Ferrit CM choke, ≥ 1mH, 3A |
| TVS | Transient enerji yutma | SMBJ58A / SMCJ58A (daha yüksek enerji) |
| FET | Ters polarite + OV + inrush | **Koruma kontrolcüsü + high-side N-FET** (D-09). GND'de FET yok |
| Bulk | Giriş ripple ve transient tampon | ≥ 63V elektrolitik / polimer |

GND-side N-FET elendi. P-FET+zener elendi — aynı işlev, daha az karakterize.

### 1.4 Ele alınması gereken saha koşulları

| Koşul | Önlem | Doküman |
|-------|-------|---------|
| Ters polarite | High-side N-FET, kontrolcü (D-09) | bu doküman |
| Aşırı gerilim | Kontrolcü OV kesme + TVS | bu doküman |
| Surge / transient | TVS + CM choke, tam uyum için kademeli ön kat | [08](08-emc-koruma.md) |
| ESD | TVS + klemens yerleşimi | [08](08-emc-koruma.md) |
| Kısa devre | Sigorta (sistem) + slot load switch (node) | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |
| Brownout | MCU BOR + node'ların reset'te tutulması | [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) |
| Ani yük değişimi | Bulk + slot başına soft-start | §2, [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |

---

## 2. Rail topolojisi

### Karşılaştırma

| Seçenek | Node maliyeti | EMI | Değerlendirme |
|---------|----------------|-----|---------------|
| Backplane'e ham 12–48V, her node'da geniş girişli buck | 8 × ~$1.20 | 8 ayrı yüksek dV/dt kaynağı | Pahalı ve gürültülü. K1'i ihlal ediyor. |
| Sadece +5V dağıt | 8 × ~$0.15 | Tek anahtarlama kaynağı | Röle ve analog çıkış node'ları saha gerilimi bulamaz |
| **İkili rail** | Çoğu node'da ~$0.15 | Tek ana kaynak | **Esnek ve ucuz** |

### Karar: tek ray — sadece +5V · D-08 (revize)

| Rail | Gerilim | Kaynak | Kullanım |
|------|---------|--------|----------|
| **+5V** | 5V ±%3 | Host'ta tek verimli geniş girişli senkron buck | **Tüm node'lar.** Node 5V→3.3V için ucuz LDO/buck kullanır |

> **VBUS_RAW (12–48 V) dağıtımı kaldırıldı.** İlk taslakta backplane'e ham
> giriş gerilimi de dağıtılıyordu. Uçtan uca sorgulandığında tek gerçek
> müşterisinin henüz tasarlanmamış bir node tipi (analog çıkış 0–10 V
> compliance) olduğu görüldü. O node'a ~$0.30'luk lokal boost koymak, sekiz
> slota iki pin + backplane boyunca yüksek gerilim dağıtmaktan ucuz ve güvenli.
> Gerekçelerin tamamı:
> [04 §5.3](04-backplane-mekanik.md#53-neden-26-değil-12-tarihsel-karşılaştırma)

**Tek ray olmasının kazançları:**

| Kazanç | Detay |
|--------|-------|
| 2 backplane pini | 26 → 12 pin sadeleşmesinin parçası |
| **Backplane tamamen SELV** | Yüksek gerilim yok — izolasyon ve creepage derdi yok |
| Node güç katı basitleşti | Tek giriş, 5V→3.3V tek regülatör |
| Host güç katı basitleşti | VBUS_RAW dağıtımı, sigortalaması ve slot limiti ortadan kalktı |

**Bobin gerilimi bir bağımlılık değil.** 5 V'tan yüksek bobin gerekiyorsa
yükseltme **node üzerinde** yapılır — 5V→12V küçük bir boost ya da kapasitif
gerilim katlayıcı, ~$0.20–0.30. Bu, tek ray kararını **koşulsuz** hale
getiriyor: parça tedariği kararı geri açamaz.

> Not: Bobin **gücü** gerilimden bağımsız. 12/24 V + boost, 5 V tarafta
> P/η. İri 32/64 A bobin 1–3 W → 5 V'ta yüzlerce mA darbe (D-68 tavan 800 mA).

---

## 3. Ana dönüştürücü

| Parametre | Değer |
|-----------|-------|
| Giriş | 12–48V (ön kat sonrası ≤ 55V) |
| Çıkış | 5V |
| Tasarım akımı | **2.0 A sürekli (10 W)** · 🟢 D-31 |
| Topoloji | **Senkron** buck |
| Akım limiti | **≥ 3.0 A** — büyük röle darbesi (§5) |
| Gerilim sınıfı | 60V |
| Anahtarlama frekansı | 300–500 kHz (verim / boyut dengesi) |

### Neden 2.0 A — ne 1.5 A ne 3 A

1.5 A, Ethernet host'tan çıkınca kesilmişti. Az: 16–64 A latching + **12/24 V
bobin + boost** anlık 5 V akımını büyütür; COM Ethernet 1U'da 150 mA'yi zorlar.

3 A / 15 W, 60 °C'de 2 katmanı yakar (§6). **2.0 A net sayı** — sürekli tavan;
darbe 3 A limitte, sıralı (D-68). İlk PCB'de bobin darbesi ölçülür; SKU 800 mA
@5 V'u aşarsa ray büyümez, o node 2U veya daha yavaş sıra.

```
Buck sürekli          2.0 A     host + node (D-31)
  Host rezerv         0.4 A     Wi-Fi tepe
  Node havuzu         1.6 A     descriptor toplamı (D-29)
1U tavan              250 mA
2U tavan              500 mA
Buck akım limiti      3.0 A     20–50 ms darbe
Tek bobin tepe        ≤ 800 mA  @5 V — 16–64 A, 5/12/24 V + boost
```

### Senkron neden zorunlu

Non-senkron buck'ta 48V→5V dönüşümde catch diyot çevrimin ~%90'ında iletir:

```
P_diyot = Vf × Iout × (1 − D)
        = 0.5V × 2A × 0.90
        = 0.90 W       ← tek başına, sadece diyotta
```

Senkron alt FET (R_DSon ≈ 20mΩ) ile:

```
P_altFET = I² × R_DSon × (1 − D)
         = 4 × 0.020 × 0.90
         = 0.07 W
```

**~0.8W tasarruf.** §5'teki termal analiz göz önüne alındığında bu fark
belirleyici.

### 3.1 Hafif yük verimi · D-48

**Sistem zamanının %90'ından fazlasını 50–200 mA çekerek geçiriyor**
([10 §5](10-enerji-butcesi.md#5-güç-durumu-bütçeleri)). CCM-only ~%50; PFM ~%85.

**Tam yük verimi neredeyse hiç kullanılmıyor.** Ayrıntı [10 §7.2](10-enerji-butcesi.md#72-dönüştürücü-seçim-kriterleri--d-48).

### 3.2 İki dönüştürücülü yapı · D-42

Ana buck tek başına yeterli değil: S3 depo modunda 25 µA mertebesinde Iq
gerekiyor ve 2A için optimize edilmiş bir dönüştürücü bunu veremiyor.

```
12–48V ─┬─→ Housekeeping buck  3.3V / 500 mA / Iq ≤ 25 µA   ── sürekli açık
        └─→ Ana buck           5V / 2A / EN pinli, senkron, PFM  ── S3'te kapalı
```

Gerekçe ve hesap: [10 §7.1](10-enerji-butcesi.md#71-iki-dönüştürücülü-yapı)

### 3.3 3.3V rail

5V → 3.3V, ESP32 WiFi TX tepe akımı 350mA.

LDO ile: `(5.0 − 3.3) × 0.65A = 1.1W` — 2 katmanda küçük paket için fazla.
**Buck kullanılacak.** ESP32'nin temiz besleme ihtiyacı için LC filtre + yerel
bulk eklenecek.

---

## 4. Güç bütçesi

### 4.1 Slot başına (+5V)

| Node tipi | Tipik | Maksimum |
|------------|-------|----------|
| Dijital giriş (8 kanal) | 30 mA | 80 mA |
| Dijital çıkış (8 kanal) | 50 mA | 120 mA |
| Analog giriş (8 kanal) | 60 mA | 200 mA |
| COM Ethernet | 120 mA | 250 mA |
| Röle lojiği (sürekli) | 20 mA | 80 mA |
| Röle bobini (anlık, sıralı) | — | **≤ 800 mA @5 V** · §5 |

Sürekli tavan ENABLE / descriptor. Bobin darbesi bu tavanın **üstünde** —
D-68 sıralar, buck 3 A limit yer.

### Tahsis · D-29

| | +5V sürekli |
|--|-------------|
| **1U** | **250 mA (1.25 W)** |
| **2U** | **500 mA (2.5 W)** |
| **Node havuzu** | **≤ 1.6 A** (descriptor toplamı — 8×250 sığmaz, host 0.4 A) |
| Aşan node | 2U (D-61 ile aynı taşma) |

2U elektrik yalnız sol konnektörden ([04 §7](04-backplane-mekanik.md#7-2u-node-stratejisi)
· D-16). 500 mA sürekli + 800 mA darbe, 2 × +5V gold finger (1–3 A/kontak)
içinde.

### 4.2 Host kartı

| Blok | Akım | Güç |
|------|------|-----|
| ESP32-S3 — Wi-Fi kapalı (varsayılan, D-65) | 40 mA @3.3V | 0.13 W |
| ESP32-S3 — Wi-Fi TX tepe (talep üzerine) | 350 mA @3.3V | 1.16 W |
| İzole RS-485 (xcvr + izole DC-DC) | 40 mA @5V | 0.20 W |
| PCA9555 + LED'ler + misc | 60 mA @3.3V | 0.20 W |
| **Host toplam (5V'tan)** | | **~0.4 W tipik / ~1.6 W tepe** |

> Host'ta Ethernet yok (D-47) — önceki sürümdeki W5500 + magjack satırı (0.50 W)
> bütçeden çıkarıldı.

### 4.3 Sistem toplamı

```
Node havuzu tavanı (D-29)          =   1.6 A  =  8.0 W
Host Wi-Fi tepesi                  =   0.4 A  =  2.0 W
                                      ───────
+5V sürekli tavan                  =   2.0 A  = 10 W   · D-31
Akım limiti (röle darbe)           =   3.0 A            (§5)

Giriş @ %87, 10 W çıkış            =  11.5 W
    @ 12 V  →  0.96 A     ← boyutlandırma
    @ 24 V  →  0.48 A
    @ 48 V  →  0.24 A

Giriş sigortası                    =  2.5 A yavaş  (§1.3) — 12 V'ta pay bol
```

Tipik S1/S2: 0.1–0.2 A ([10 §5](10-enerji-butcesi.md#5-güç-durumu-bütçeleri)).
2 A ENABLE en kötü durum, boşta tüketim değil.

### 4.4 Güç bütçesi zorlaması

Bütçe kâğıt üzerinde kalmıyor — **donanımla zorlanıyor.** Node descriptor'ı
beyan ettiği tüketimi içeriyor; host, bütçe aşılıyorsa node'un reset'ini
bırakmıyor.

Ayrıntı: [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) ve
[05 §7](05-dahili-bus.md#7-fonksiyon-kodları).

---

## 5. Anlık akım — röle darbeleri

Sürekli tüketim düşük, ama **röle bobinleri anlık olarak rayı zorlayabilir.**
Tek ray kararının doğrudan sonucu, bu yüzden ayrı hesaplanıyor. · D-68

### 5.1 Bobin başına 5 V tarafı akımı

Bobin **gücü** gerilimden bağımsız; 12/24 V + boost 5 V akımını ≈1/η kadar
artırır. Asıl sıçrama **büyük kontak**: 8 A ~0.3 W değil, 32/64 A 1–3 W.

```
P_bobin 1.5 W, 12/24 V, boost %80
I_5V = 1.5 / 0.80 / 5  ≈  375 mA

P_bobin 3.0 W (iri güç rölesi)
I_5V                   ≈  750 mA
```

**Tavan: 800 mA @5 V / bobin.** İlk PCB'de ölçülür. Aşan SKU rayı büyütmez.

5 V bobin bulunmak zorunda değil — 12/24 V + lokal boost serbest (D-08, D-61).

### 5.2 Rafın tepe akımı

```
Temel (node havuzu + host, sürekli)              ≤  2.0 A

A) Rafta aynı anda 1 bobin (yürürlük)
   +800 mA  →  tepe ≤ 2.8 A     3 A limit içinde ✓

B) 8 node SYNC ile aynı anda
   8 × 800 mA                    →  kırılır ✗

C) Bir 4ch node eşzamanlı
   4 × 800 mA                    →  kırılır ✗
```

### 5.3 Neden bulk bu işi çözemiyor

C'yi kapasitörle yutmak hâlâ onlarca mF. Sıralama yapısal (D-68).

### 5.4 Karar: sıralama mimaride, kapasitör kenarda

| Katman | Kural |
|--------|-------|
| **Node içi** | Kanallar eşzamanlı ateşlenmez (~2 ms) |
| **Node'lar arası** | Röle SYNC'te değil, tarama sırasında — rafta **tek bobin** |
| **Donanım yedeği** | Buck limiti **≥ 3.0 A** |
| **Load switch** | Trip **≥ 1.5 A** — 250+800 mA darbeyi kısa sanmasın (D-23) |
| **Node bulk** | Kenar (di/dt), ~100 µF; darbenin tamamı değil |
| **Host bulk** | 5 V çıkış düşümünü sınırlar |

### 5.5 Descriptor

| Alan | Byte | Not |
|------|------|-----|
| Sürekli tüketim | 2 | mA @5V — ENABLE tavanı |
| **Tepe darbe** | **2** | mA @5V — host sıralamayı buna göre zamanlar |

## 6. Termal analiz

**Ortam sıcaklığı: 60 °C** · 🟢 D-04 — karavan, kapalı mekân, güneş altında
50 °C rahat görülür. **Pasif soğutma · D-57** — fan yok. Host buck için doğal
konveksiyon + bakır döküm; node ısısı Al kızağa
([04 §6](04-backplane-mekanik.md#6-hava-akışı-ve-termal)).

**Host girişi 12–48 V · D-69** — 12 V leisure ve 48 V ESS aynı ön kat.

### 6.1 Ana buck kaybı — iki senaryo

```
EN KÖTÜ DURUM (tüm slotlar tepe)
    Çıkış  10 W  ·  verim ~%86  →  kayıp ≈ 1.36 W

GERÇEKÇİ SÜREKLİ (S1/S2)
    Çıkış  0.5–2 W  ·  PFM       →  kayıp ≈ 0.1–0.3 W
```

Enerji bütçesi mimarisi sayesinde **sürekli çalışma noktası en kötü durumun
onda biri.** Termal tasarım en kötü duruma göre yapılır ama gerçek hayatta
oraya nadiren gidilir.

### 6.2 60 °C'de ne oluyor

| Stackup | θ_ja (geniş döküm) | ΔT @1.36W | Junction @60°C | Değerlendirme |
|---------|--------------------|-----------|----------------|---------------|
| 2 katman | ~40 °C/W | 54 °C | **114 °C** | Sınırda — 125 °C sınırına 11 °C marj |
| 4 katman + termal via | ~25 °C/W | 34 °C | **94 °C** | Rahat — 31 °C marj |

### 6.3 Sonuç

**2 katman en kötü durumda çalışır, ama marjı dar.** Bu artık bir zorunluluk
değil, bir marj tercihi — ayrıntı ve karar
[08 §5](08-emc-koruma.md#5-katman-sayısı-kararı).

> **Not:** 3 A / 15 W hâlâ 2 katmanı 60 °C'de yakar. 2.0 A kilit (D-31) o
> sınırı aşmaz; 1.5 A'e kesmek gerekmedi — büyük bobin için 2 A zaten doğru.
