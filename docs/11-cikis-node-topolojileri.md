# 11 — Çıkış Node'u Topolojileri

Çıkış anahtarlama teknolojisi seçimi. Batarya beslemeli bir sistemde bu, bir
konfor tercihi değil **enerji bütçesi kararıdır**.

---

## 1. Kontrol enerjisi — asıl karşılaştırma

Tartışma genelde "MOSFET mi röle mi" diye kurulur. Doğru soru: **yük açıkken
anahtarı o durumda tutmak ne kadar enerji harcıyor?**

| Teknoloji | Tutma gücü / kanal | Anahtarlama enerjisi | Durum korunur mu? |
|-----------|--------------------|--------------------|-------------------|
| Monostabil röle | **200–500 mW** | — | Hayır |
| MOSFET, high-side (charge pump) | **25–40 mW** | ~µJ | Hayır |
| MOSFET, low-side | ~0 | ~µJ | Hayır |
| **Latching (bistabil) röle** | **0** | 5–25 mJ / geçiş | **Evet** |

### 1.1 Günlük enerji — 8 kanal, günde 8 saat açık

```
Monostabil röle     8 × 0.30 W × 8 h   =  19.2 Wh/gün
MOSFET high-side    8 × 0.03 W × 8 h   =   1.9 Wh/gün
MOSFET low-side     ~0                 =   ~0
Latching röle       8 × 10 geçiş × 15 mJ = 0.0003 Wh/gün  ≈ 0
```

**Referans: tüm sistemin günlük tüketimi 5.5 Wh**
([10 §6.1](10-enerji-butcesi.md#61-gerçekçi-kullanım-günü)).

| Teknoloji | Sistem bütçesine oranı |
|-----------|------------------------|
| Monostabil röle | **%350 — sistemin 3.5 katı** |
| MOSFET high-side | **%35** |
| Latching röle | **%0.005** |

### 1.2 Sonuç: sezgi doğru, ama gerekçe farklı

> "Herkes MOSFET diyor, ben latching'in daha düşük tükettiğini düşünüyorum."

**Doğru — ama şartlı.** Kritik detay şu: **MOSFET'in sıfır tutma gücü sadece
low-side anahtarlamada geçerli.**

Karavanda yüklerin ezici çoğunluğu **şasi toprağına bağlı** (lambalar, pompalar,
fanlar). Bu yükler **high-side anahtarlanmak zorunda** — artı ucu kesilir.
High-side N-MOSFET ise gate'i kaynak geriliminin üzerinde tutmak için **sürekli
çalışan bir charge pump** gerektiriyor.

```
Akıllı high-side anahtar (PROFET sınıfı), ON durumunda:  3–5 mA @12V
8 kanal                                                =  ~0.3 W sürekli
```

**Latching rölede bu sıfırdır.** Kalıcı mıknatıs tutuyor — devre yok, akım yok.

Yani: *low-side MOSFET = latching = 0*, ama **high-side MOSFET ≈ latching'in
sonsuz katı** ve karavanda gereken high-side.

---

## 2. Kontrol enerjisi dışındaki eksenler

Karar sadece enerjiyle verilemez.

| Kriter | MOSFET | Latching röle |
|--------|--------|---------------|
| Anahtarlama çevrimi | **Sınırsız** | 10⁴–10⁶ |
| **PWM / kısma** | **Evet** — dimmer, fan hızı, pompa soft-start | Hayır |
| Anahtarlama hızı | µs | 5–15 ms |
| Galvanik izolasyon | Yok | **Var** |
| AC anahtarlama | Hayır (back-to-back gerekir) | **Evet** |
| **DC ark kesme** | **Sorun yok** | **Zor — sıfır geçişi yok** |
| Kapalıyken kaçak | µA seviyesi | **Sıfır** |
| Arıza modu | **Genelde KISA DEVRE — yük açık kalır** | Genelde açık (kontak kaynaması mümkün) |
| Titreşim (K5) | Etkilenmez | **Şok değeri kontrol edilmeli** |
| Güç kesintisinde durum | Kaybolur | **Korunur** |

### 2.1 "Herkes neden MOSFET diyor?" — teknik sebebi

**DC ark kesme.** AC her yarım periyotta sıfırdan geçer, ark kendiliğinden
söner. DC'de böyle bir şey yok — 48V/32A bir kontağı açtığınızda ark sürekli
beslenir, kontakları eritir.

Yüksek akımlı DC için ark üfleme mıknatıslı, kutup yönüne duyarlı özel
kontaktörler gerekir; pahalı ve hacimli. MOSFET'te ark diye bir olgu yok.

**Yani "MOSFET" tavsiyesi enerjiyle ilgili değil, ark ve ömürle ilgili.** İkisi
farklı sorular ve ikisinin de cevabı doğru — hangi yükten bahsettiğinize bağlı.

---

## 3. Hibrit anahtar — ikisini birden almak

Yüksek akımlı DC için her iki dünyanın avantajı:

```
Latching röle kontağı  ──┬── yük
                         │
MOSFET ──────────────────┘   (kontağa paralel)

AÇMA sırası:
   1. MOSFET iletime geçer          (akım MOSFET'e kayar)
   2. Röle kontağı açılır           (üzerinden akım geçmiyor → ARK YOK)
   3. MOSFET kesime geçer

KAPAMA sırası:
   1. MOSFET iletime geçer          (akımı o alır)
   2. Röle kontağı kapanır          (soğuk kapanma → kontak aşınması yok)
   3. MOSFET kesime geçer

SÜREKLİ DURUM:
   Röle kontağı taşır · MOSFET kapalı · bobin akımı SIFIR
```

| Kazanç | |
|--------|---|
| Tutma gücü | **0** (latching) |
| Ark | **Yok** (MOSFET devralıyor) |
| Kontak aşınması | **Yok** (soğuk anahtarlama) → çevrim ömrü çok artar |
| İletim kaybı | Kontak direnci (MOSFET'ten düşük olabilir) |
| İzolasyon | **Var** |

Maliyet: kanal başına ~$4–6. **32A ve 64A DC kanallar için önerilen topoloji.**
Elektrikli araç ve solar kontaktörlerinde standart yaklaşım.

---

## 4. DC / AC ayrımı

### Karar: ayrı node aileleri, AC minimum 2U

Bu bir tercih değil, fiziksel zorunluluk:

| Gerekçe | Detay |
|---------|-------|
| **Creepage / clearance** | 230V AC ile SELV (12–48V) arasında takviyeli izolasyon için ≥5.5 mm creepage. **17.5 mm'lik bir 1U node'da** lojik + izolasyon + çok kanal yan yana sığmıyor |
| **Güvenlik** | Şebeke ve SELV'in aynı kartta bulunması tüm kartı şebeke sınıfına sokuyor |
| **Klemens** | Farklı akım sınıfı, farklı adım (7.5 / 10 mm), yanlış bağlantıyı önlemek için farklı renk ve kodlama |
| **Arıza modu** | Şebeke tarafı arızası SELV tarafına geçmemeli |

**AC node'ları 2U.** Şebeke PCB adası klipsli bariyer (D-64); kablo IP20 fiş
(D-38). Tam kutu yok.

### 4.1 Sıfır geçişi (zero-cross) · D-55

**Sıfır geçişi:** 230 V sinüs 0 V'tan geçerken röleyi çekmek. O anda akım ≈ 0,
kontak kıvılcımı küçük, ömür uzun.

Karavan AC çoğu zaman **inverter** (kare / MSW) — düzgün sıfır yok; yanlış
anda kesmek daha kötü.

**Kural:** sinüs (şebeke / iyi inverter) → sıfırda kes. İnverter / bozuk dalga
algılanırsa **rastgele + RC snubber.** Snubber her zaman var. Opto, 230 V
adasında (D-64).

---

## 5. Katalog (çıkış) · D-72

Ayrıntı ve analog/COM: [09 §5](09-node-aileleri.md#5-node-katalogu).

**Tek teknoloji / node.** MOSFET DO **8 × 8 A, 1U** — 8 A latching yok.
PWM aynı MOSFET. Güç/AC **1U veya 2U, 4U yok.**

### 5.1 DC çıkış

| SKU | Form | Kanal | Akım | Teknoloji |
|-----|------|-------|------|-----------|
| **DO-M-8A-8** | 1U | **8** | 8 A (eşzamanlı tavan ~32 A) | High-side MOSFET + PWM |
| **DC-L-16A-4** | 1U* | 4 | 16 A | Latching |
| **DC-H-32A-2** | 2U | 2 | 32 A | Hibrit |
| **DC-H-64A-2** | 2U | 2 | 64 A | Hibrit — 48 V ark |

\* 1U hedef; röle >14.4 mm → 2U, kanal 4 (D-61).

### 5.2 AC çıkış

AC **yalnız 2U** (D-51). 8 × 16 A tek gövdede 4U olurdu → **4 kanal.**

| SKU | Form | Kanal | Akım |
|-----|------|-------|------|
| **AC-L-16A-4** | 2U | 4 | 16 A latching |
| **AC-L-32A-2** | 2U | 2 | 32 A latching |

### 5.3 Klemens · D-38

Pluggable yaylı. Adım kablo sınıfına göre — hepsi 3.5 mm değil.

```
Sinyal + 8 A DO  3.5 mm     5 kutup / 17.5 mm   (2.5 mm²; 4 mm² yok)
16 A             5.08–6.35 mm
32 A             7.5 mm, 6 mm²
64 A             10–12 mm
AC               7.5 / 10 mm
```

---

## 6. İletim kaybı ve termal

Kontrol enerjisi çözüldü; geriye **iletim kaybı** kalıyor. Bu, kanal sayısını
belirleyen gerçek kısıt.

```
MOSFET   :  P = I² × R_DSon
Kontak   :  P = I² × R_kontak
```

| Akım | MOSFET (tipik R_DSon) | Kayıp | Kontak (tipik) | Kayıp |
|------|----------------------|-------|----------------|-------|
| 8 A | 2 mΩ | 0.13 W | 3 mΩ | 0.19 W |
| 32 A | 1 mΩ | 1.02 W | 2 mΩ | 2.05 W |
| 64 A | 0.8 mΩ | 3.28 W | 0.5 mΩ (kontaktör) | 2.05 W |

> ⚠️ Kontak direnci değerleri **doğrulanmalı**. Datasheet'ler genelde "başlangıç
> ≤100 mΩ" gibi kötümser değerler verir; gerçek oturmuş değer çok daha düşüktür
> ama parçaya göre değişir. Parça seçiminde ölçülmüş/tipik değer aranacak.

### 6.1 Termal sınır — kanal sayısını belirleyen şey

Gerçek node ölçüleri ([12 §1.3](12-mekanik-referans-rev01.md#13-node-ölçüleri)):
**17.5 × 80 × 110 mm**, 60 °C ortam.

> ⚠️ **Düzeltme.** Bu bölümün ilk hali, node'un serbest havada tek başına
> durduğunu varsayıyordu. Yanlıştı — 8 node yan yana paketlenmiş, **yan
> yüzeyler komşu node'a bakıyor, havaya değil.**

```
SERBEST HAVA (yanlış varsayım)
    Yüzey = 2(80×110) + 2(17.5×110) + 2(17.5×80)  =  0.0243 m²

PAKETTE (doğru) — sadece ön panel + üst/alt kenar serbest
    Etkin yüzey ≈ (17.5×80) + 2(17.5×110)          =  0.0053 m²

                                                      5× fark
```

Doğal konveksiyon katsayısı ≈ 7 W/m²K:

| Node | Kayıp | ΔT (paket) | İç sıcaklık @60°C |
|-------|-------|------------|-------------------|
| DO-M-8A-8, 3 kanal 8 A (eşzamanlı) | ~1.5 W | 41 °C* | *yalnız hava; Al kızak şart |
| DO-DC-32A-H, 2 kanal | 4.1 W | 110 °C | **170 °C** ✗✗ |

**Sonuç: paketlenmiş 1U'da yalnız havaya bakan yüzey yetmez.** Fan yok
(D-57). Isı Al kızak/şasi ve (yüksek akımda) metal ön panel üzerinden çıkar.
ΔT bu yola sığmayan node spec'te 2U olur veya kanal düşer — fan geri gelmez.

### 6.2 Pasif soğutma — fan yok · D-57

Zorlamalı hava ürün kararı değil. Termal, node dissipasyon tavanının ve
şasi iletiminin işi.

**Doğal uyum:** Latching ve MOSFET tutma gücü sıfıra yakın; yük yokken ısı yok.
Yük varken ısı Al yola gitmek zorunda.

### 6.3 Isı yolu · D-54

**32 A / 64 A:** Al kızak (birincil) **+ metal ön panel** yayıcı. PCB bakır
yetmez. 8 A MOSFET'te panel metal şart değil (kızak yeter).

| Önlem | Rol |
|-------|-----|
| Al kızak → şasi | Birincil iletim (D-57, D-62) |
| **Metal ön panel** | 32/64 A yayıcı · D-54 |
| Eşzamanlılık derecesi | Spec'te yazılır |
| Node NTC | Aşırı ısınmada kanal kesilir |
| Kör kapak | Baca (D-63) |

> Bu hesaplar kaba tahmindir; gerçek kutu geometrisi ve hava akışıyla CFD veya
> prototip ölçümü ile doğrulanmalıdır.

---

## 7. Latching röle sürüşü — pratik detaylar

### 7.1 Bobin tipi

| Tip | Sürüş | Değerlendirme |
|-----|-------|---------------|
| **Çift bobin** (set + reset) | Kanal başına 2 transistör | **Basit** — ULN2803 sınıfı dizi sürücü yeterli |
| Tek bobin (kutup ters çevirmeli) | Kanal başına H-köprü | Daha az bobin, daha karmaşık sürüş |

**Öneri: çift bobin.** 8 kanal = 16 sürüş hattı → shift register + darlington
dizi. Node MCU'sunda GPIO yakmıyor, maliyeti düşük.

### 7.2 Darbe yönetimi — kritik tasarım notu

```
Büyük latching (32/64 A) 1–3 W, 10–30 ms
12/24 V bobin + boost %80 → **5 V tarafı ≤ 800 mA** (D-68)

5 V bobin zorunlu değil. 4 kanal AYNI ANDA:
    4 × 800 mA  =  3.2 A  →  3 A buck limiti aşılır
```

**Kural: röle darbeleri sıralanır; rafta aynı anda tek bobin.** ~2 ms node
içi; tarama node'lar arası (~600 µs). SYNC ile röle yok. İlk PCB'de ölçüm:
SKU 800 mA @5 V'u aşarsa ray büyümez.

### 7.3 Durum geri okuma · D-53

**Tüm latching SKU: yardımcı kontak.** Gerilim ölçümü yok — yüksüz yanıltır;
AC'de 230 V MCU'ya gelmez.

Açılışta kör darbe yok. Aux okunur, yazılım kontağa uydurulur.

### 7.3.1 Glitch heal · D-77

Anlık VIN/5 V git-gellerinde sistem **iyileşir**, kör kesmez.

| Çıkış | Glitch (anahtar ON) | S3 (anahtar OFF) |
|-------|---------------------|------------------|
| **Latching** | Mıknatıs tutar. Aux gerçek. Host yazılımı aux'a hizalanır | Kontak durur. Kör reset yok |
| **MOSFET DO / AO** | Charge pump ölür → çıkış düşer. Host **kalıcı proses imajı** yazar; ray dönünce geri yükler | İsteyerek kapalı. ON'da host imajı yükler |

S3 ≠ glitch. Depo bilinçli; glitch heal ON iken.

### 7.4 Titreşim (K5)

Latching rölenin durumu kalıcı mıknatısla tutuluyor. **Şok/titreşim altında
konum değiştirme riski var.**

```
Karavan yol titreşimi           ≈  < 5 g
Tipik latching röle fonksiyonel şok değeri  ≈  10–20 g
```

> **Parça seçim:** bobin 5 V serbest (tek ray). Yükseklik 1U'da 14.4 mm'ye
> sığmazsa node **2U** (D-61) — alçak profil avı zorunlu değil. Şok değeri
> ayrıca doğrulanır.

Marj yeterli görünüyor **ama parça seçiminde şok değeri açıkça doğrulanacak** —
bu, gözden kaçarsa sahada "kendiliğinden kapanan lamba" olarak geri döner.

---

## 8. Arıza modu ve güvenlik

| Teknoloji | Tipik arıza | Sonuç |
|-----------|-------------|-------|
| MOSFET | **Kısa devre** (termal kaçış) | **Yük kapatılamaz** — ısıtıcı/vinç için tehlikeli |
| Röle kontağı | Kaynama (daha nadir) | Yük kapatılamaz |
| Röle bobini | Açık devre | Yük anahtarlanamaz (güvenli taraf) |

### 8.1 Mimari sonuç: ana kesici bir güvenlik yedeği

**DO-DC-64A-H (ana batarya kesici) yalnızca bir çıkış node'u değil, tüm
sistemin güvenlik yedeğidir.** Herhangi bir MOSFET kanalı kısa devre arızası
verirse, ana kesici tüm DC dağıtımı kesebilir.

Bu, 64 A node'u "opsiyonel yüksek akım kanalı" olmaktan çıkarıp **güvenlik
mimarisinin parçası** yapıyor.

> Isıtıcı, vinç gibi gözetimsiz çalışabilen yükler için tek bir MOSFET kanalına
> güvenilmemeli — seri bir latching/kontaktör kesici önerilir.

---

## 9. Açık sorular

| ID | Soru |
|----|------|
| ~~D-52~~ | ✅ **Karara bağlandı:** ayrı node'lar, her node 4 kanal ve tek teknoloji ([§5.1](#51-dc-çıkış)) |
| D-53 | ✅ **Yardımcı kontak**, tüm latching (gerilim ölçümü yok) |
| D-54 | ✅ **Al kızak + metal ön panel** (32/64 A) |
| D-55 | ✅ Sinüste sıfır geçişi; inverter'de rastgele + snubber |
