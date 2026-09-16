# 10 — Enerji Bütçesi

> **Bu doküman master tasarımının en kritik kısıtıdır.** Diğer tüm master
> kararları bununla çelişiyorsa yeniden değerlendirilir.

---

## 1. Neden birincil kısıt

NeoPLC'nin hedef uygulaması **karavan yönetimidir**. Bu, şebeke beslemeli bir
endüstriyel panodan iki temel farkla ayrılıyor:

| | Endüstriyel pano | Karavan |
|---|---|---|
| Enerji kaynağı | Şebeke — pratikte sınırsız | **Batarya — sonlu ve pahalı** |
| Boşta tüketim | Önemsiz | **Ürünün yaşayabilirliğini belirliyor** |
| Kullanılmadığı süre | Yok, sürekli çalışır | **Aylarca depoda park halinde** |

### 1.1 Referans batarya

```
Tipik karavan leisure bataryası    100 Ah @ 12 V  =  1200 Wh
Kullanılabilir (%50 DoD)           600 Wh
```

Bu sayı, aşağıdaki her bütçe kaleminin ölçüldüğü referanstır.

---

## 2. Mevcut tasarımdaki çelişki

[05](05-dahili-bus.md)'te tanımlanan 200 Hz polling mimarisi, **modüllerin hiç
uyuyamaması** anlamına geliyor — master her 4.8 ms'de bir cevap bekliyor.

```
8 modül × MCU sürekli uyanık (10 mA @3.3V)  =  80 mA  =  264 mW
Günlük                                       =  6.3 Wh/gün
```

Batarya bağlamında bu kabul edilemez. **Polling mimarisi enerji bütçesine düşman
olarak tasarlanmıştı.** Bu doküman o çelişkiyi çözüyor.

### 2.1 Tarama hızı gerçekte ne olmalı?

200 Hz, endüstriyel varsayımdan geliyordu. Karavan yükleri için gerçek gereksinim:

| Fonksiyon | Gereken tepki |
|-----------|---------------|
| Aydınlatma anahtarı | < 100 ms (insan algısı) |
| Su pompası | < 200 ms |
| Sıcaklık / batarya izleme | saniyeler |
| Kapı / hareket sensörü | < 100 ms |

**10 Hz (100 ms) tüm ihtiyaçları karşılıyor.** 200 Hz, 20× gereksiz enerji
harcaması demekti.

### Karar: uyarlanabilir tarama hızı · 🟡 D-40

| Durum | Tarama | Gerekçe |
|-------|--------|---------|
| Aktif | 20 Hz | Kullanıcı etkileşimi sırasında akıcı tepki |
| Boşta | 10 Hz | Varsayılan çalışma |
| Bekleme | 1 Hz | Park halinde, sadece izleme |
| Depo | — | Modüller tamamen kapalı |

---

## 3. Wake-on-bus: modüllerin uyuması

### Karar · 🟡 D-41

```
Modül MCU'su STOP modunda uyur              (~2 µA)
RS-485 alıcısı açık kalır                   (~0.5 mA — zorunlu, master'ı duymalı)
USART start-bit ile MCU'yu uyandırır
Modül çerçeveyi işler, cevap verir, tekrar uyur
```

**Duty cycle hesabı:**

```
Uyanık süre / işlem        ≈  600 µs   ([05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi))

10 Hz'de:  duty = 600 µs × 10 / 1 s     =  0.6 %
Ortalama  = 0.006 × 10 mA  +  0.5 mA    =  0.56 mA @3.3V  =  1.85 mW

Karşılaştırma (sürekli uyanık)           =  10.5 mA  =  34.6 mW
                                            ─────────────────────
Kazanç                                       18×
```

8 modül için: **277 mW → 15 mW.**

### 3.1 Neden RS-485 alıcısı kapatılmıyor

Alıcı kapatılırsa modül master'ı duyamaz — uyandırmak için ayrı bir donanım
hattı gerekir. Maliyeti hesaplayalım:

```
8 × 0.5 mA @3.3V  =  13 mW  =  0.32 Wh/gün
```

Bekleme durumunda bile toplam bütçenin küçük bir kısmı. **Ek donanım hattı ve
uyandırma gecikmesi karmaşıklığına değmiyor.**

> **Parça seçim kriteri:** Transceiver seçiminde **alıcı boşta akımı** birincil
> kriterdir. Bazı RS-485 transceiver'ları 2 mA çekiyor — bu 4× fark demek.

---

## 4. Güç durumları

### Karar · 🟡 D-39

| Durum | Tetikleyici | Master | Modüller | Hedef |
|-------|-------------|--------|----------|-------|
| **S0 Aktif** | Kullanıcı bağlı / otomasyon çalışıyor | WiFi açık, Ethernet açık, 20 Hz | Wake-on-bus | ~1.4 W |
| **S1 Boşta** | N dakika etkileşim yok | WiFi modem-sleep, **Ethernet kapalı**, 10 Hz | Wake-on-bus | ~0.43 W |
| **S2 Bekleme** | Park, aktivite yok | WiFi kapalı, 1 Hz | Wake-on-bus | ~60 mW |
| **S3 Depo** | Kullanıcı komutu / uzun hareketsizlik | ESP32 deep sleep | **Tamamen kapalı** | ~1.3 mW |

### 4.1 S3 — mevcut kararların beklenmedik yakınsaması

S3'ü mümkün kılan iki mekanizma **zaten başka gerekçelerle** tasarlanmıştı:

| Mekanizma | Asıl gerekçesi | S3'teki rolü |
|-----------|----------------|--------------|
| **MOD_RST# varsayılan pull-down** ([06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu)) | Güç bütçesi zorlaması | Modülleri µA seviyesine indirir |
| **Slot başına load switch** ([06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması)) | Arıza izolasyonu + hot-plug soft-start | Modülleri **tamamen** beslemeden keser |

S3 için yeni donanım gerekmiyor — var olan iki mekanizma birlikte kullanılıyor.

---

## 5. Güç durumu bütçeleri

### S0 — Aktif

| Kalem | Akım | Güç |
|-------|------|-----|
| ESP32-S3, WiFi aktif | 120 mA @3.3V | 396 mW |
| W5500 + magjack, link up | 150 mA @3.3V | 495 mW |
| İzole RS-485 saha portu | 40 mA @5V | 200 mW |
| PCA9555, LED, backplane xcvr | 20 mA @3.3V | 66 mW |
| 8 modül (20 Hz, wake-on-bus) | — | 30 mW |
| Dönüşüm kayıpları (~%15) | — | 179 mW |
| **Toplam** | | **~1.37 W** |

### S1 — Boşta

| Kalem | Güç |
|-------|-----|
| ESP32-S3, modem-sleep (DTIM3) | 82 mW |
| **W5500 — güç kesildi** | **0** |
| İzole RS-485 saha portu | 200 mW |
| PCA9555, LED, backplane xcvr | 66 mW |
| 8 modül (10 Hz) | 15 mW |
| Dönüşüm kayıpları | 64 mW |
| **Toplam** | **~0.43 W** |

### S2 — Bekleme

| Kalem | Güç |
|-------|-----|
| ESP32-S3, light sleep, 1 Hz uyanma | 7 mW |
| WiFi kapalı, Ethernet kapalı | 0 |
| RS-485 saha portu kapalı | 0 |
| Backplane xcvr + expander | 10 mW |
| 8 modül (1 Hz) | 15 mW |
| Dönüşüm + Iq | 28 mW |
| **Toplam** | **~60 mW** |

### S3 — Depo

| Kalem | Güç @48V | Güç @12V |
|-------|----------|----------|
| ESP32-S3 deep sleep (10 µA @3.3V) | 33 µW | 33 µW |
| Housekeeping regülatör Iq (25 µA) | 1.20 mW | 0.30 mW |
| Ana buck — devre dışı | 0 | 0 |
| Modüller — beslemesiz | 0 | 0 |
| **Toplam** | **~1.3 mW** | **~0.35 mW** |

---

## 6. Günlük ve mevsimlik enerji

```
S0   1.37 W   →  32.9 Wh/gün
S1   0.43 W   →  10.3 Wh/gün
S2   0.06 W   →   1.44 Wh/gün
S3   0.0013 W →   0.031 Wh/gün
```

### 6.1 Gerçekçi kullanım günü

```
S0  2 saat  =  2.74 Wh
S1  4 saat  =  1.72 Wh
S2 18 saat  =  1.08 Wh
              ────────
              5.54 Wh/gün

600 Wh kullanılabilir batarya  →  108 gün
```

### 6.2 Kış deposu (90 gün, S3)

```
90 gün × 0.031 Wh  =  2.8 Wh     →  bataryanın %0.5'i
```

### 6.3 Naif tasarımla karşılaştırma

| | Naif (her şey açık, 200 Hz) | Bu tasarım |
|---|---|---|
| Günlük | 32.9 Wh | **5.5 Wh** |
| Batarya ömrü (kullanımda) | 18 gün | **108 gün** |
| 90 günlük depo | **2960 Wh — batarya ölür** | 2.8 Wh |

**6× kullanımda, 1000× depoda.**

---

## 7. Güç mimarisine etkisi

### 7.1 İki dönüştürücülü yapı · 🟡 D-42

Tek bir 3A buck ile S3'e inilemiyor — 3A için optimize edilmiş bir
dönüştürücünün boştaki Iq'su ve hafif yük verimi kötü.

```
12–48V ─┬─→ Housekeeping buck  3.3V / 500 mA / Iq ≤ 25 µA  ── sürekli açık
        │      → ESP32-S3, PCA9555, backplane transceiver
        │
        └─→ Ana buck  5V / 3A / EN pinli, senkron, PFM     ── S3'te kapalı
               → slot load switch'leri → modüller
               → izole RS-485 saha portu
```

**Kazanç:** S3'te Iq 25 µA (1.2 mW @48V) vs tek-buck yaklaşımında ~50 mW.
**~40× fark**, 90 günlük depoda 108 Wh vs 2.8 Wh.

Ek maliyet: ~$0.80. Batarya ömrü karşısında tartışmasız.

### 7.2 Dönüştürücü seçim kriterleri — değişti

Enerji bütçesi, parça seçim önceliklerini tersine çeviriyor:

| Eski öncelik | Yeni öncelik |
|--------------|--------------|
| Tam yükte (3A) tepe verim | **Hafif yükte (50–200 mA) verim — PFM / pulse-skipping zorunlu** |
| Maliyet | **Boşta akım (Iq)** |
| Boyut | Maliyet |

**Gerekçe:** Sistem zamanının %90'ından fazlasını S1/S2'de, yani 50–200 mA
çekerek geçiriyor. Sadece CCM çalışan bir buck bu bölgede %50 verimde olabilir;
PFM destekleyen bir buck %85. **Tam yük verimi neredeyse hiç kullanılmıyor.**

### 7.3 Güç kapısı gereksinimleri

| Yük | Kapılama | Gerekçe |
|-----|----------|---------|
| **W5500 + magjack** | Load switch (3.3V) | **Tek en büyük sürekli yük — 495 mW** |
| İzole RS-485 saha portu | Load switch (5V) | 200 mW, sürekli Modbus RTU gerekmiyorsa kapatılır |
| Slotlar | Mevcut slot load switch'leri | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |

---

## 8. Ethernet'in enerji maliyeti

Brief'te Ethernet + Modbus TCP zorunlu tutulmuştu. Karavan bağlamında bunun
bedeli açıkça ortaya konmalı:

```
W5500 + magjack, link up     =  495 mW
Sürekli açık bırakılırsa     =  11.9 Wh/gün
600 Wh bataryanın            =  %2 / gün

Bu tek başına, tüm sistemin geri kalanının yaklaşık 2 katı.
```

**Öneri: W5500 varsayılan olarak kapalı.** Kullanıcı kablolu bağlantı istediğinde
(veya link algılandığında) açılır, S1'e geçişte kapanır.

> **Değerlendirmene sunuyorum:** Karavanda Ethernet gerçekten gerekli mi, yoksa
> WiFi yeterli mi? Gerekliyse bu tasarım onu destekliyor — sadece varsayılan
> kapalı. Gerekmiyorsa W5500 ve magjack BOM'dan çıkar, master kartı belirgin
> şekilde basitleşir ve [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı)'teki
> yerleşim kısıtı ortadan kalkar.

---

## 9. Karavan bağlamının getirdiği yeni gereksinimler

Bu üçü endüstriyel varsayımda yoktu, batarya sisteminde zorunlu.

### 9.1 Batarya izleme · 🟡 D-43

Master, VBUS_RAW gerilimini ölçmeli.

```
VBUS_RAW ──[ direnç böleni ]──→ ESP32 ADC
```

Maliyet: 2 direnç + 1 kapasitör. Sağladıkları:

- Batarya durumu raporlama (Modbus + web UI)
- **Düşük gerilim uyarısı ve yük atma** — bataryayı derin deşarjdan koruma
- Brownout öngörüsü ([03 §1.4](03-guc-mimarisi.md#14-ele-alınması-gereken-saha-koşulları))
- S2 → S3 geçişi için otomatik tetikleyici

**Düşük gerilim kesme (LVD), bir batarya sisteminde isteğe bağlı değildir.**
Derin deşarj bataryayı kalıcı olarak öldürür — korunan varlık, ürünün
kendisinden pahalı.

### 9.2 Uyandırma kaynakları · 🟡 D-44

S3'ten çıkış için donanım tetikleyicileri gerekiyor:

| Kaynak | Uygulama |
|--------|----------|
| RTC periyodik | ESP32 dahili — saatte bir batarya/sıcaklık kontrolü |
| Şebeke/şarj algılama | Dijital giriş — karavan prize takıldı |
| Kontak/ateşleme | Dijital giriş — araç çalıştı |
| Kapı / hareket | Dijital giriş |
| Kullanıcı butonu | Master ön yüzünde |

En az **2 adet uyandırma girişi** master'da ayrılmalı (ESP32 RTC GPIO'larından).

### 9.3 Titreşim · 🟡 D-45

**Karavan hareketli bir araçtır.** Bu, endüstriyel DIN pano varsayımında olmayan
bir mekanik gereksinim.

| Risk | Önlem |
|------|-------|
| Kart kenarı konnektöründe fretting korozyonu | Modül tutucu (mandal veya vida) — konnektör tek başına tutmamalı |
| Ağır bileşenlerin yorulması | Elektrolitik kapasitör, indüktör, magjack için ek mekanik destek veya düşük profilli parça tercihi |
| Klemens gevşemesi | Push-in yaylı klemens tercih edilmeli ([09 §4](09-modul-aileleri.md#4-saha-bağlantısı)) — vidalı klemens titreşimde gevşer |

Bu, [04](04-backplane-mekanik.md)'teki mekanik standardı etkiliyor: **modül
tutma mekanizması pinout kadar bağlayıcı bir standart.**

---

## 10. Firmware sorumlulukları

Enerji bütçesi donanım kararı olduğu kadar firmware kararıdır.

| Gereksinim | Açıklama |
|------------|----------|
| Durum makinesi | S0–S3 geçişleri, zaman aşımları kullanıcı tarafından ayarlanabilir |
| Ölçüm | Gerçek tüketim VBUS_RAW akımından ölçülebilmeli (opsiyonel shunt) |
| Raporlama | Modbus register'larında durum + tahmini batarya ömrü |
| Modül uyku koordinasyonu | Master, tarama hızı değişimini modüllere bildirmeli |
| Güvenli geçiş | S3'e geçmeden önce çıkışlar tanımlı duruma alınmalı |

> **Uyarı:** S3'te modüller beslemesiz. Bu, **çıkışların durumunu kaybetmesi**
> demek. Bir röle S3'te açık kalamaz. S3'e geçiş, tüm çıkışların güvenli
> (kapalı) duruma alınabildiği durumlarda mümkün — bu, kullanıcının anlaması
> gereken bir davranış ve web UI'da açıkça belirtilmeli.
