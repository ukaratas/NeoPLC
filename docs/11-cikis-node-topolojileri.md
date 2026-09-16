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
| **Creepage / clearance** | 230V AC ile SELV (12–48V) arasında takviyeli izolasyon için ≥5.5 mm creepage. 22.5 mm'lik bir 1U node'da lojik + izolasyon + çok kanal yan yana sığmıyor |
| **Güvenlik** | Şebeke ve SELV'in aynı kartta bulunması tüm kartı şebeke sınıfına sokuyor |
| **Klemens** | Farklı akım sınıfı, farklı adım (7.5 / 10 mm), yanlış bağlantıyı önlemek için farklı renk ve kodlama |
| **Arıza modu** | Şebeke tarafı arızası SELV tarafına geçmemeli |

**AC node'ları 2U.** Karavanda AC zaten yalnızca şebeke bağlıyken veya inverter
çalışırken var — kanal sayısı ihtiyacı DC'ye göre çok daha az.

---

## 5. Önerilen node ailesi

### 5.1 DC çıkış

**Tasarım kuralı: her node tek teknoloji, 4 kanal.** Karışık node yok — daha
basit, daha modüler, stok ve üretim yönetimi kolay · D-52.

| Node | Form | Kanal | Akım | Teknoloji | Hedef yük |
|-------|------|-------|------|-----------|-----------|
| **DO-DC-8A-L** | 1U | **4** | 8 A | **Latching röle** | Buzdolabı, ısıtıcı, sabit aydınlatma — **saatlerce açık kalanlar** |
| **DO-DC-8A-M** | 1U | **4** | 8 A | **MOSFET** (akıllı high-side) | Dimmer'lı aydınlatma, fan hızı, pompa soft-start — **PWM gerekenler** |
| **DO-DC-32A-H** | 2U | 2 | 32 A | **Hibrit** | Inverter beslemesi, su ısıtıcı, klima |
| **DO-DC-64A-H** | 2U | 1 | 64 A | **Hibrit / kontaktör** | Ana batarya kesici, vinç, şarj hattı |

**Ayrım kuralı:** Yük PWM/kısma gerektiriyorsa MOSFET, gerektirmiyorsa latching.
Bu, senin "8A / 32A / 64A MOSFET" önerinden farkım: **8A sınıfının çoğunluğu
latching olmalı**, çünkü karavanda bu sınıftaki yükler saatlerce açık kalıyor ve
tam da §1'deki 0.3 W'lık charge pump maliyetinin biriktiği yer burası.

### 5.2 AC çıkış

| Node | Form | Kanal | Akım | Teknoloji | Not |
|-------|------|-------|------|-----------|-----|
| **DO-AC-16A-L** | 2U | **3** | 16 A | Latching röle | 16 A = standart şebeke girişi sınıfı |
| **DO-AC-32A-L** | 2U | 2 | 32 A | Latching röle | Yüksek güç / ana AC hat |

AC'de latching tartışmasız doğru: sıfır tutma gücü **ve** AC'de ark kesme zaten
kolay (sıfır geçişi var).

### 5.3 Klemens yerleşimi kontrolü

Slot adımı 17.5 mm ([12 §3.1](12-mekanik-referans-rev01.md#31-slot-adımı-175-mm-kabul-edilmeli))
→ 1U ön panel 17.5 mm, 2U ön panel **35 mm**.

```
1U — DC 8A, 4 kanal
    3.5 mm push-in  →  17.5 / 3.5 = 5 kutup
    4 çıkış + 1 ortak dönüş = 5 kutup            ✓ tam oturuyor

2U — DC 32A, 2 kanal
    2 × (IN + OUT) = 4 kutup, 8.5 mm adım = 34 mm  ✓

2U — DC 64A, 1 kanal
    IN + OUT = 2 kutup, 12 mm adım = 24 mm         ✓

2U — AC 16A, 3 kanal
    3 × L + N = 4 kutup, 7.5 mm adım = 30 mm       ✓

2U — AC 32A, 2 kanal
    2 × L + N = 3 kutup, 10 mm adım = 30 mm        ✓
```

> **4 kanal / 1U tam oturuyor** — 3.5 mm push-in klemensle 5 kutup tam 17.5 mm
> ediyor. Slot adımının 17.5 mm'ye inmesi kanal sayısını 8'den 4'e düşürdü, ama
> "her node tek teknoloji" kararıyla birlikte bu aslında daha temiz bir yapı:
> **her node tek işi yapıyor.**

> **AC'de kanal sayısı düştü.** 2U = 35 mm (45 değil), bu yüzden 16 A'de 4 değil
> **3 kanal** sığıyor. Şebeke klemensleri tek sıra olmalı — iki sıra yüksek akım
> için güvenli değil.

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
| DO-DC-8A-L, 8 kanal | 1.5 W | 41 °C | **101 °C** ✗ |
| DO-DC-32A-H, 2 kanal | 4.1 W | 110 °C | **170 °C** ✗✗ |

**Sonuç: paketlenmiş blade mimarisinde doğal konveksiyon yetmiyor.**

### 6.2 Zorlamalı soğutma zorunlu

Çalışma draftının arka panelinde fan bulunması bu yüzden doğru bir karardı
([12 §3.5](12-mekanik-referans-rev01.md#35-soğutma-fan-ve-benim-termal-hatam)).

Fan ile kanal başına hava akışı sağlandığında etkin ısı transferi katsayısı
20–40 W/m²K'ya çıkıyor — yukarıdaki ΔT değerleri 3–6 kat düşüyor.

**Ama fan enerji bütçesiyle çatışıyor** (0.5–1.5 W, sistemin 2–6 katı).
Çözüm: termostatik kontrol · 🟡 D-57 —
[12 §3.5](12-mekanik-referans-rev01.md#fanın-enerji-bütçesine-etkisi-yeni-çakışma).

**Doğal uyum:** Isı yalnızca çıkışlar yük sürerken oluşuyor. Latching ve MOSFET
tutma gücü sıfıra yakın olduğundan, yük yokken ısı da yok, fan da gerekmiyor.
Fan sadece gerçekten gerektiğinde çalışıyor.

### 6.3 Ek termal önlemler

| Önlem | Etki |
|-------|------|
| Alüminyum ray/kılavuz ısı yolu olarak kullanılması | Node'un ısısını host gövdesine aktarır — draft'taki hibrit yapı buna uygun |
| Eşzamanlılık derecelendirmesi | "2 kanal 32 A, ancak aynı anda tek kanal tam yük" |
| Güç node'larının fan akışına yakın slotlara yerleştirilmesi | Host firmware'i slot tipini bildiği için kullanıcıya öneri verebilir |
| Node içi sıcaklık sensörü | Aşırı ısınmada kanalı kendisi kapatır — descriptor yetenek bayrağı |

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
Bobin darbesi:  12V × 30 mA × 20 ms  =  7.2 mJ / geçiş

8 kanal AYNI ANDA anahtarlanırsa:
    8 × 30 mA  =  240 mA anlık
    Slot VBUS_RAW limiti  =  500 mA   ([03 §4](03-guc-mimarisi.md#4-güç-bütçesi))
```

Sığıyor, **ama** aynı anda ateşleme rail'de dip yaratır ve komşu slotları
etkileyebilir.

**Kural: röle darbeleri sıralanmalı (staggered), asla eşzamanlı ateşlenmemeli.**
Node firmware'inin sorumluluğu. Örneğin 2 ms arayla → tüm kanallar 16 ms'de
tamamlanır, tepe akım 30 mA'de kalır.

Node üzerinde bobin darbelerini besleyen yerel bir tampon kapasitör de
eklenmeli — darbe akımını backplane yerine kapasitörden çekmek rail'i korur.

### 7.3 Durum geri okuma

Latching röle **durumunu kaybetmez, ama yazılım kaybedebilir** — node reset
olduğunda röle hâlâ eski konumunda.

**Zorunlu: kontak durumu geri okunabilmeli.** Yardımcı kontak veya çıkış
geriliminin ölçülmesi ile. Aksi halde node açılışta rölenin durumunu bilemez ve
kör bir "reset" darbesi atmak zorunda kalır — bu da sessiz bir yük kesintisi
demek.

Bu, descriptor'daki **yetenek bayrakları**na girmeli
([05 §7.1](05-dahili-bus.md#71-node-descriptorı-identify-yanıtı)).

### 7.4 Titreşim (K5)

Latching rölenin durumu kalıcı mıknatısla tutuluyor. **Şok/titreşim altında
konum değiştirme riski var.**

```
Karavan yol titreşimi           ≈  < 5 g
Tipik latching röle fonksiyonel şok değeri  ≈  10–20 g
```

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
| D-52 | 8 A sınıfında latching ve MOSFET **iki ayrı node mü**, yoksa tek node'da karışık mı? Ayrı olması üretimi ve stoğu basitleştirir; karışık olması kullanıcıya esneklik verir. |
| D-53 | Kontak durumu geri okuma yöntemi: yardımcı kontak mı, çıkış gerilimi ölçümü mü? İkincisi daha ucuz ama yük bağlı değilse yanıltıcı. |
| D-54 | 32 A / 64 A node'larda ısı yolu: alüminyum ön panel, kutu gövdesi, yoksa sadece PCB bakırı mı? |
| D-55 | AC node'larında sıfır geçişinde anahtarlama (zero-cross) uygulanacak mı? Kontak ömrünü uzatır, ek zamanlama devresi ister. |
