# 10 — Enerji Bütçesi

> **Bu doküman host tasarımının en kritik kısıtıdır.** Diğer tüm host
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

[05](05-dahili-bus.md)'te tanımlanan 200 Hz polling mimarisi, **node'ların hiç
uyuyamaması** anlamına geliyor — host her 4.8 ms'de bir cevap bekliyor.

```
8 node × MCU sürekli uyanık (10 mA @3.3V)  =  80 mA  =  264 mW
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

### Karar: uyarlanabilir tarama · D-40

200 Hz yok. 20 / 10 / 1 Hz.

| Durum | Tarama | Gerekçe |
|-------|--------|---------|
| Aktif | 20 Hz | Kullanıcı etkileşimi sırasında akıcı tepki |
| Boşta | 10 Hz | Varsayılan çalışma |
| Bekleme | 1 Hz | Park halinde, sadece izleme |
| Depo | — | Node'lar tamamen kapalı |

---

## 3. Wake-on-bus: node'ların uyuması

### Karar: STOP + start-bit · D-41

```
Node MCU'su STOP modunda uyur              (~2 µA)
RS-485 alıcısı açık kalır                   (~0.5 mA — zorunlu, host'u duymalı)
USART start-bit ile MCU'yu uyandırır
Node çerçeveyi işler, cevap verir, tekrar uyur
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

8 node için: **277 mW → 15 mW.**

### 3.1 Neden RS-485 alıcısı kapatılmıyor

Alıcı kapatılırsa node host'u duyamaz — uyandırmak için ayrı bir donanım
hattı gerekir. Maliyeti hesaplayalım:

```
8 × 0.5 mA @3.3V  =  13 mW  =  0.32 Wh/gün
```

Bekleme durumunda bile toplam bütçenin küçük bir kısmı. **Ek donanım hattı ve
uyandırma gecikmesi karmaşıklığına değmiyor.**

> **Parça seçim kriteri · D-49:** Alıcı boşta **≤ 0.5 mA** birincil; **glitch-free
> power-up/down** zorunlu (D-24). Shutdown / RE kapatma yok — node host'u her an
> duymalı. 2 mA sınıfı parçalar elenir (8 slotta 4×). SKU şemada seçilir.

---

## 4. Güç durumları

### Karar

| Durum | Tetikleyici | Host | Node'lar | Hedef |
|-------|-------------|--------|----------|-------|
| **S0 Aktif** | Kullanıcı bağlı / otomasyon çalışıyor | WiFi açık, 20 Hz | Wake-on-bus | ~1.4 W |
| **S1 Boşta** | N dakika etkileşim yok | WiFi kapalı, **BLE advertising** (D-67), 10 Hz | Wake-on-bus | ~0.43 W |
| **S2 Bekleme** | Park, aktivite yok | WiFi kapalı, **BLE advertising**, 1 Hz | Wake-on-bus | ~60 mW |
| **S3 Depo** | **Anahtar OFF** (D-44) | ESP32 deep sleep, **BLE kapalı** | **Tamamen kapalı** | ~1.3 mW |

### 4.1 S3 — mevcut kararların beklenmedik yakınsaması

S3'ü mümkün kılan iki mekanizma **zaten başka gerekçelerle** tasarlanmıştı:

| Mekanizma | Asıl gerekçesi | S3'teki rolü |
|-----------|----------------|--------------|
| **MOD_RST# varsayılan pull-down** ([06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu)) | Güç bütçesi zorlaması | Node'ları µA seviyesine indirir |
| **Slot başına load switch** ([06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması)) | Arıza izolasyonu + hot-plug soft-start | Node'ları **tamamen** beslemeden keser |

S3 için yeni donanım gerekmiyor — var olan iki mekanizma birlikte kullanılıyor.

---

## 5. Güç durumu bütçeleri

> **Ethernet çıkarıldı.** W5500 host kartında yok — §8 ve
> [02 §2](02-host-mimarisi.md#2-ethernet-hosttan-çıkarıldı).

### S0 — Aktif

| Kalem | Akım | Güç |
|-------|------|-----|
| ESP32-S3, WiFi aktif | 120 mA @3.3V | 396 mW |
| İzole RS-485 saha portu | 40 mA @5V | 200 mW |
| PCA9555, LED, backplane xcvr | 20 mA @3.3V | 66 mW |
| 8 node (20 Hz, wake-on-bus) | — | 30 mW |
| Dönüşüm kayıpları (~%15) | — | 104 mW |
| **Toplam** | | **~0.80 W** |

### S1 — Boşta

> **WiFi bu durumda KAPALI** · D-65 — [02 §3.1](02-host-mimarisi.md#31-wifi-neden-varsayılan-kapalı)

| Kalem | Güç |
|-------|-----|
| ESP32-S3, light sleep + 10 Hz uyanma, **WiFi kapalı** | 12 mW |
| İzole RS-485 — güç kapılı, görev çevrimli | 20 mW |
| PCA9555, LED, backplane xcvr | 66 mW |
| 8 node (10 Hz) | 15 mW |
| Dönüşüm kayıpları | 15 mW |
| **Toplam** | **~0.13 W** |

> **S1'de artık "misc" (66 mW) baskın kalem.** WiFi ve RS-485 kapatıldıktan
> sonra sıradaki hedef PCA9555 + LED'ler + backplane transceiver. LED'lerin
> görev çevrimli sürülmesi buradan ~30 mW daha alabilir.

> **S1'de RS-485 artık baskın yük.** Ethernet gittikten sonra sıradaki en büyük
> kalem o. Bu yüzden izole beslemesi güç kapılı olmalı
> ([§7.3](#73-güç-kapısı-gereksinimleri)) — sürekli açık bırakılırsa S1
> tüketimi 0.21 W yerine 0.39 W olur, neredeyse iki katı.

### S2 — Bekleme

| Kalem | Güç |
|-------|-----|
| ESP32-S3, light sleep, 1 Hz uyanma | 7 mW |
| WiFi kapalı, Ethernet kapalı | 0 |
| RS-485 saha portu kapalı | 0 |
| Backplane xcvr + expander | 10 mW |
| 8 node (1 Hz) | 15 mW |
| Dönüşüm + Iq | 28 mW |
| **Toplam** | **~60 mW** |

### S3 — Depo

| Kalem | Güç @48V | Güç @12V |
|-------|----------|----------|
| ESP32-S3 deep sleep (10 µA @3.3V) | 33 µW | 33 µW |
| Housekeeping regülatör Iq (25 µA) | 1.20 mW | 0.30 mW |
| Ana buck — devre dışı | 0 | 0 |
| Node'lar — beslemesiz | 0 | 0 |
| **Toplam** | **~1.3 mW** | **~0.35 mW** |

---

## 6. Günlük ve mevsimlik enerji

```
S0   0.80 W   →  19.2 Wh/gün
S1   0.13 W   →   3.1 Wh/gün
S2   0.06 W   →   1.44 Wh/gün
S3   0.0013 W →   0.031 Wh/gün
```

### 6.1 Gerçekçi kullanım günü

WiFi talep üzerine açıldığı için S0 artık kısa ve seyrek:

```
S0  0.5 saat  =  0.40 Wh     (kullanıcı telefondan bağlanıyor)
S1  5.5 saat  =  0.72 Wh
S2 18   saat  =  1.08 Wh
                ────────
                2.20 Wh/gün

600 Wh kullanılabilir batarya  →  273 gün
```

### 6.2 Kış deposu (90 gün, S3)

```
90 gün × 0.031 Wh  =  2.8 Wh     →  bataryanın %0.5'i
```

### 6.3 Naif tasarımla karşılaştırma

| | Naif (her şey açık, 200 Hz, Ethernet) | Bu tasarım |
|---|---|---|
| Günlük | 32.9 Wh | **2.2 Wh** |
| Batarya ömrü (kullanımda) | 18 gün | **273 gün** |
| 90 günlük depo | **2960 Wh — batarya ölür** | 2.8 Wh |

**15× kullanımda, 1000× depoda.**

Kazancın kaynakları:

| Değişiklik | Katkı |
|------------|-------|
| Ethernet'in çıkarılması | 11.9 Wh/gün |
| WiFi'ın talep üzerine açılması | 1.3 Wh/gün |
| Wake-on-bus (node'lar uyuyor) | 6.3 Wh/gün |
| Tarama hızı 200 → 10 Hz | (yukarıdakinin ön koşulu) |
| S2 / S3 güç durumları | Deponun tamamı |
| İki dönüştürücülü yapı | S3'te 40× |

---

## 7. Güç mimarisine etkisi

### 7.1 İki dönüştürücülü yapı · D-42

Tek bir 2 A buck ile S3'e inilemiyor — 2 A için optimize edilmiş dönüştürücünün
boşta Iq'su ve hafif yük verimi kötü (D-48).

```
12–48V ─┬─→ Housekeeping buck  3.3V / 500 mA / Iq ≤ 25 µA  ── sürekli açık
        │      → ESP32-S3, PCA9555, backplane transceiver
        │
        └─→ Ana buck  5V / 2.0 A / EN pinli, senkron, PFM   ── S3'te kapalı
               → slot load switch'leri → node'lar
               → izole RS-485 saha portu
```

**Kazanç:** S3'te Iq 25 µA (1.2 mW @48V) vs tek-buck yaklaşımında ~50 mW.
**~40× fark**, 90 günlük depoda 108 Wh vs 2.8 Wh.

Ek maliyet: ~$0.80. Batarya ömrü karşısında tartışmasız.

### 7.2 Dönüştürücü seçim kriterleri · D-48

Parça seçim sırası ters: zamanın %90'ı S1/S2, **50–200 mA**.

| Eski | Kilit |
|------|-------|
| Tam yük tepe verim | **Hafif yük / PFM** |
| Maliyet önce | **Iq** (boşta akım) |
| Boyut | Sonra maliyet |

CCM-only buck bu bölgede ~%50; PFM ~%85. 2 A %94 neredeyse hiç kullanılmaz.

### 7.3 Güç kapısı gereksinimleri

| Yük | Kapılama | Gerekçe |
|-----|----------|---------|
| **Wi-Fi radyosu** | Yazılımdan kapatılır (varsayılan kapalı, D-65) | **En büyük değişken yük — S0'da 396 mW** |
| İzole RS-485 saha portu | Load switch (5V) | 200 mW, sürekli Modbus RTU gerekmiyorsa kapatılır |
| Slotlar | Mevcut slot load switch'leri | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |

---

## 8. Ethernet kararı

Brief'te Ethernet + Modbus TCP zorunlu tutulmuştu. Karavan bağlamında bedeli
hesaplandı ve **host kartından çıkarılmasına karar verildi** · D-47.

```
W5500 + magjack, link up     =  495 mW
Sürekli açık bırakılırsa     =  11.9 Wh/gün
Sistemin geri kalanı         =  ~3.5 Wh/gün
                                ──────────────
Tek başına sistemin 3.4 katı
```

**RS-485 aynı işi 2 telle ve çok daha ucuza yapıyor:**

| | Ethernet (W5500) | RS-485 2 tel |
|---|---|---|
| Sürekli tüketim | **495 mW** | 200 mW izole · **~3 mW** izolesiz |
| Kablo | 4–8 telli RJ45 | **2 tel + GND** |
| BOM | ~$3 | ~$0.20 |
| Boşta kapatılabilir | Link düşer | **Evet, sorunsuz** |

**Modbus TCP kaybolmuyor** — WiFi üzerinden sunuluyor. Kablolu Ethernet gerçekten
gerekirse **haberleşme node'u olarak** takılıyor: ihtiyaç yoksa enerjisi hiç
ödenmiyor ([02 §2.2](02-host-mimarisi.md#22-ethernet-bir-node-olarak)).

Bu kararın tetiklediği zincir:

```
Ethernet çıktı
   ├─→ 11.9 Wh/gün tasarruf        (bütçe 5.5 → 3.5 Wh/gün)
   ├─→ 6 GPIO serbest              (batarya ölçümü, uyandırma, sıcaklık)
   ├─→ 25 mm yerleşim kısıtı gitti
   ├─→ Host sürekli tavan 2.0 A kilit (D-31; büyük bobin + COM)
   └─→ 2 katman host uygulanabilir (D-05)
```

---

## 9. Karavan bağlamının getirdiği yeni gereksinimler

Bu üçü endüstriyel varsayımda yoktu, batarya sisteminde zorunlu.

### 9.1 Batarya izleme + LVD · D-43

Host **VIN** ölçer (12–48 V, D-69). 2 direnç + ADC.

- Batarya raporu (Modbus / UI)
- **LVD:** uyarı + yük atma — derin deşarj yasak
- Brownout öngörüsü

**S3'e otomatik inmez** (D-44: S3 yalnız anahtar OFF). LVD, anahtar ON iken
yükleri keser / uyarı verir; depo modu değil.

LVD isteğe bağlı değil — korunan varlık üründen pahalı.

### 9.2 Güç anahtarı ve uyandırma · D-44

**Aç-kapa düğmesi var** (ön panel, latching). VIN kesici değil — housekeeping
her zaman VIN görür.

| Anahtar | VIN | Davranış |
|---------|-----|----------|
| **ON** | Var | Cihaz **açık**: S0 / S1 / S2. Boşta S3'e **inmez**. "Enerji varken hep açık" bu. |
| **OFF** | Var | **S3** (~1 mW). Node'lar kesik. Şarj/şebeke gelirse uyanır. |
| — | Yok | Ölü. VIN gelince: anahtar ON ise açılır; OFF ise S3'te kalır ta ki şarj veya ON. |

S3 uyandırma (2 RTC GPIO):

| Pin | İş |
|-----|-----|
| 1 | Aç-kapa (ON kenarı) |
| 2 | Şarj / şebeke algılama |

Wi-Fi butonu **ayrı** (D-65) — güç anahtarı değil, 10 dk AP.
**BLE advertising** S1/S2'de açık, **S3'te kapalı** (D-67). Depoyu yemez.

Kontak/kapı host'a çekilmez; gerekirse DI-8 (sistem zaten ON).

### 9.3 Titreşim

**Karavan hareketli bir araçtır.** Bu, endüstriyel DIN pano varsayımında olmayan
bir mekanik gereksinim.

| Risk | Önlem |
|------|-------|
| Kart kenarı konnektöründe fretting korozyonu | **Kapalı vida** (D-45) — 1U: 1, 2U: 2. Konnektör tek başına tutmaz |
| 2U sola yaslanma / burulma | Sağ bakırsız yalancı dil (D-16) — arkada ikinci yatak; vidanın yerine geçmez |
| Ağır bileşenlerin yorulması | Elektrolitik kapasitör, indüktör, magjack için ek mekanik destek veya düşük profilli parça tercihi |
| Klemens gevşemesi | Push-in yaylı klemens tercih edilmeli ([09 §4](09-node-aileleri.md#4-saha-bağlantısı)) — vidalı klemens titreşimde gevşer |

Bu, [04 §3.3](04-backplane-mekanik.md#33-takma--çıkarma)'teki standart:
**kapalı vida, pinout kadar bağlayıcı.** Hot-plug sök-tak; vida tutma.

---

## 10. Firmware sorumlulukları · D-50 (oturumda)

Enerji bütçesi donanım kararı olduğu kadar firmware kararıdır. Durum makinesi
S0–S3 (D-39/D-44) ve glitch heal (D-77) **donanımda kilitli**; kod firmware
oturumunda.

| Gereksinim | Açıklama |
|------------|----------|
| Durum makinesi | S0–S3 geçişleri, zaman aşımları kullanıcı tarafından ayarlanabilir |
| Ölçüm | Gerçek tüketim VIN akımından ölçülebilmeli (opsiyonel shunt) |
| Raporlama | **Host API** (D-78) — durum + tahmini batarya ömrü |
| Node uyku koordinasyonu | Host, tarama hızı değişimini node'lara bildirmeli |
| Güvenli geçiş | S3'e bilinçli iniş. Latching aux ile durur; MOSFET/AO host imajına (D-77) |
| Glitch heal · D-77 | ON iken kısa VIN/5 V kesisi: latching aux; DO/AO host'tan geri yazılır |

> **S3 ≠ glitch.** S3'te latching kontak **açık kalabilir** (mıknatıs). MOSFET
> kapanır. ON'a dönüşte host kalıcı imajı yükler (D-77). Kör röle darbesi yok.
