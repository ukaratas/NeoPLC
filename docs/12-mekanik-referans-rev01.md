# 12 — Mekanik Referans (Çalışma Draftı Rev 0.1)

Bu doküman, mimari çalışmadan **önce** hazırlanmış fiziksel tasarım draftını
kayıt altına alır ve mevcut mimari kararlarla çakışmalarını işaretler.

**Statü:** Referans. Bağlayıcı değil — ama bazı kalemlerde draft mevcut
önerilerden **daha iyi** ve benimsenmesi öneriliyor.

---

## 1. Draft'tan alınan somut veriler

### 1.1 Terminoloji

Draft **Host / Node** kullanıyor; mimari dokümanlar **Host / Node**.

> **🟡 D-56 — Terminoloji birleştirilmeli.** Draft senin kendi ürün dilin
> olduğu için Host/Node'a geçmeyi öneriyorum. Onaylarsan tüm dokümanlarda
> toplu değiştiririm.

### 1.2 Host ölçüleri

| Ölçü | Değer |
|------|-------|
| Genişlik (dış) | 310.0 mm |
| Yükseklik | 120.0 mm |
| Derinlik | 80.0 mm |
| İç genişlik | 252.0 mm |
| **Slot adımı** | **17.50 mm** |
| 8 slot toplam | 8 × 17.50 = 140.00 mm |

### 1.3 Node ölçüleri

| | 1U | 2U |
|---|-----|-----|
| Genişlik | **17.50 mm** | **35.00 mm** |
| Yükseklik | 80.0 mm | 80.0 mm |
| Derinlik | 110.0 mm | 110.0 mm |

### 1.4 Backplane pinout (draft)

```
GND (uzun)   24V   5V   3.3V   SDA   SCL   INT   RST
BST   ID0   ID1   ID2   FAULT   DETECT
```

Mate kademesi: **Uzun pin = GND · Orta pin = Power · Kısa pin = Signal** (3 kademe)

### 1.5 Diğer

| Kalem | Draft |
|-------|-------|
| Besleme girişi | 24V DC |
| Backplane rail | 24V / 5V / 3.3V |
| Haberleşme (dış) | WiFi (ESP32) · Ethernet · RS485 · USB-C |
| Hot-swap | Destekli |
| Mekanik kilit | **Var** — kilit kapalı / açık mandal |
| Montaj | Kızak rayı + yan kılavuz, önden tak-kilitle |
| Yapı | 3D baskı + alüminyum ray hibrit |
| Soğutma | **Arka panelde fan** |
| 2U örnek | Güç röle node'u 30A / 50A |

---

## 2. Çakışma tablosu

| # | Konu | Draft Rev 0.1 | Mimari önerisi | Değerlendirme |
|---|------|---------------|----------------|---------------|
| 1 | Slot adımı | **17.50 mm** | 22.50 mm | **Draft kazanıyor** — §3.1 |
| 2 | Dahili haberleşme | **I²C** (SDA/SCL/INT) | RS-485 diferansiyel | **Mimari kazanıyor** — §3.2 |
| 3 | Besleme girişi | 24V DC | 12–48V | **Brief kazanıyor** (sonraki karar) |
| 4 | Backplane rail | 24V + 5V + 3.3V | VBUS_RAW + 5V | **Tartışmalı** — §3.3 |
| 5 | Slot adresi | 3 bit (ID0–2) | 4 bit | **Mimari öneriliyor** — §3.4 |
| 6 | SYNC hattı | Yok | Var | **Mimari öneriliyor** |
| 7 | Node derinliği | 110 mm | 90 mm (varsayım) | **Draft kazanıyor** — gerçek ölçü |
| 8 | Node yüksekliği | 80 mm | 100 mm (varsayım) | **Draft kazanıyor** — gerçek ölçü |
| 9 | Mekanik kilit | **Var** | D-45'te sonradan eklendi | **Draft kazanıyor** — zaten çözülmüş |
| 10 | Soğutma | **Fan** | Doğal konveksiyon | **Draft kazanıyor** — §3.5, benim hatam |
| 11 | Terminoloji | Host / Node | Host / Node | Draft — D-56 |

---

## 3. Çakışmaların değerlendirmesi

### 3.1 Slot adımı: 17.5 mm kabul edilmeli

22.5 mm önerim, endüstriyel DIN node genişliğine dayanıyordu. Ama **17.5 mm de
bir DIN standardıdır** — modüler şalt cihazlarının (sigorta, kontaktör) tek
kutup genişliği 17.5/18 mm'dir. Yani ekosistem argümanı her ikisi için de
geçerli.

Draft'ın kazanma sebebi:

```
8 slot × 22.5 mm  =  180 mm
8 slot × 17.5 mm  =  140 mm      →  40 mm daha dar cihaz
```

Karavanda hacim pahalı. **17.5 mm benimseniyor.**

**Bedeli — kabul edilmesi gereken:** Ön panelde klemens için 17.5 mm kalıyor.
Bu, kanal başına klemens adımını sıkıştırıyor ve yüksek akım klemensleri için
sorun:

| Klemens adımı | 17.5 mm'ye sığan | Uygun akım |
|---------------|------------------|------------|
| 3.5 mm push-in | 5 kutup | ≤ 8 A |
| 5.0 mm | 3 kutup | ≤ 16 A |
| 7.5 mm | 2 kutup | ≤ 24 A |

**Sonuç: 8 kanallı bir 1U node tek sırada mümkün değil.** İki sıra (üst/alt)
veya daha az kanal gerekiyor. Draft'ın 1U ön panelinde de zaten 2 sıra var.

→ [09 §4](09-node-aileleri.md#4-saha-bağlantısı) ve
[11 §5](11-cikis-node-topolojileri.md#5-önerilen-node-ailesi) bu kısıta göre
revize edilmeli.

### 3.2 I²C backplane: değiştirilmesi öneriliyor

Draft'ta SDA/SCL/INT var — yani **I²C tabanlı bir backplane**. Bu, mimari
çalışmada elenen yaklaşımdan bile riskli:

| Sorun | I²C'de durum |
|-------|--------------|
| Ground bounce | **Tek uçlu, TTL ile aynı zafiyet** — 8 node'un anahtarlamalı yükleri altında marj yetersiz |
| **Hot-plug** | **I²C'nin en bilinen zafiyeti.** Takma anında SDA/SCL'de oluşan glitch tüm busu kilitler; kurtarma için clock stretching hilesi veya bus reset gerekir |
| Arızalı node | Bir node SDA'yı düşük tutarsa **tüm bus ölür** — arıza izolasyonu yok |
| Adresleme | 7-bit adres, ama node'lar aynı tip ise adres çakışması yönetimi gerekir |
| Mesafe | Backplane boyunca kapasitans artıyor, hız düşüyor |

Draft hot-swap desteklediğini söylüyor; **I²C ile hot-swap, özel hot-swap buffer
IC'leri (PCA9511/9515 sınıfı) olmadan güvenilir değil** — bu da node başına
~$1 ek maliyet demek.

**RS-485 önerisi geçerliliğini koruyor** ([05 §1](05-dahili-bus.md#1-fiziksel-katman-kararı)).
Aynı 2 pin, node başına ~$0.20, ground bounce bağışıklığı, hot-plug toleransı,
arıza izolasyonu.

> **Not:** Bu, draft'ın bilgisayar destekli erken bir eskizi olmasından
> kaynaklanıyor olabilir. Backplane PHY'si mimarinin geri dönülemez
> kalemlerinden — [01 §5](01-sistem-genel-bakis.md#5-standardize-edilmesi-zorunlu-kalemler).

### 3.3 Backplane rail sayısı: 3.3V tartışmalı

Draft 24V + 5V + 3.3V dağıtıyor; mimari VBUS_RAW + 5V öneriyor.

| | Draft (3 rail) | Mimari (2 rail) |
|---|---|---|
| Node regülatörü | **Gereksiz** — 3.3V hazır | 5V→3.3V, ~$0.15 |
| Backplane pini | +2 pin | — |
| Kayıp | 3.3V hattında I×R kaybı, 8 node'a dağıtım | Node içinde kısa yol |
| Gürültü | **Tüm node'lar aynı 3.3V'u paylaşıyor** — bir node'un gürültüsü hepsine gidiyor | Her node izole |
| Esneklik | Node 3.3V'tan başka gerilim isterse yine regülatör gerekir | Her node kendi ihtiyacına göre |

**Öneri: 3.3V dağıtılmasın.** Node başına $0.15'lik regülatör, gürültü
izolasyonu ve esneklik karşılığında ucuz. Özellikle analog giriş node'larında
paylaşılan 3.3V rail'i ölçüm kalitesini düşürür.

**Ama** 3.3V dağıtımının bir avantajı var: **çok düşük güçlü node'lar
regülatörsüz yapılabilir** → K1'e hizmet ediyor. Bu yüzden pinout'ta 3.3V için
**pin rezerve edilmesi** ve v1'de kullanılmaması önerilir.

### 3.4 Slot adresi: 3 bit → 4 bit

Draft ID0–ID2 = 3 bit = 8 slot. Tam kapasitede, genişleme payı yok.

4. bit maliyeti: 1 pin + 1 direnç. Kazancı: 16 slota kadar genişleme, veya
ileride iki host'un zincirlenmesi.

**Pinout geri dönülemez olduğu için 4. bit şimdi alınmalı**
([06 §1](06-slot-yonetimi.md#1-slot-adresleme)).

### 3.5 Soğutma: fan — ve benim termal hatam

**Draft'ın arka panelinde fan var. Haklı, ve ben yanılmışım.**

[11 §6.1](11-cikis-node-topolojileri.md#61-termal-sınır-kanal-sayısını-belirleyen-şey)'deki
termal hesabım, node'un **serbest havada tek başına** durduğunu varsayıyordu.
Gerçekte 8 node yan yana paketlenmiş — **yan yüzeyler komşu node'a bakıyor,
havaya değil.**

```
YANLIŞ (serbest hava, 17.5 × 80 × 110):
   Yüzey = 2(80×110) + 2(17.5×110) + 2(17.5×80)  =  0.0243 m²
   1.5 W için ΔT ≈ 8.8 °C                            ✓ rahat

DOĞRU (pakette, sadece ön panel + üst/alt kenar serbest):
   Etkin yüzey ≈ (17.5×80) + 2(17.5×110)          =  0.0053 m²
   1.5 W için ΔT ≈ 41 °C   →  60 °C ortamda 101 °C    ✗
```

**5× fark.** Doğal konveksiyon paketlenmiş blade mimarisinde yeterli değil —
draft'ın fan kararı doğru.

#### Fan'ın enerji bütçesine etkisi — yeni çakışma

```
40 mm fan tipik tüketim        0.5 – 1.5 W
Sürekli çalışırsa (24 h)       12 – 36 Wh/gün
Tüm sistemin bütçesi           5.5 Wh/gün    ([10 §6.1](10-enerji-butcesi.md#61-gerçekçi-kullanım-günü))
```

**Fan tek başına sistemin 2–6 katı tüketebilir.** Bu, K4 ile doğrudan çatışıyor.

**🟡 D-57 — Fan termostatik kontrollü olmalı.**

```
Fan çalışma koşulu:  iç sıcaklık > eşik  VE  yük mevcut
S1 / S2 / S3'te     :  fan kapalı
```

Bu doğal bir uyum sağlıyor: ısı yalnızca **çıkışlar yük sürerken** oluşuyor
([11 §6](11-cikis-node-topolojileri.md#6-iletim-kaybı-ve-termal)). Latching
röle ve MOSFET'in tutma gücü sıfıra yakın olduğu için, yük yokken ısı da yok,
fan da gerekmiyor.

Gereksinimler:
- Host'ta sıcaklık sensörü (en az 1, tercihen backplane ortası)
- Fan PWM kontrolü (ESP32 GPIO)
- Fan arıza tespiti (tacho girişi) — fan durursa yükler kısıtlanmalı
- **Fan'ın kendisi 24V/VBUS_RAW'dan beslenmeli**, +5V_SYS'ten değil

### 3.6 Mekanik paradigma: kutu-içinde-kutu → gerçek blade

Draft'ta her node kendi plastik muhafazasında, host'un önüne takılan kapalı bir
kutu. Yani "kutuya kutular bağlanıyor".

**Bu, içinde kızakları olan gerçek bir mini blade şasisine çevrildi** · D-60.

Dört gerekçe — ayrıntı [04 §1](04-backplane-mekanik.md#1-mekanik-mimari-blade-mi-kutu-içinde-kutu-mu):

| # | Gerekçe |
|---|---------|
| 1 | **Termal** — plastik muhafaza her node'un etrafına yalıtım katmanı koyuyor (~0.2 W/mK). Blade'de PCB doğrudan hava kanalında. §3.5'teki termal problemi asıl çözen şey bu |
| 2 | **Maliyet** — muhafaza başına $2–5, 8 node'da $16–40. K1'in kaçınmamızı söylediği türden |
| 3 | **Titreşim (K5)** — kızak PCB'yi 110 mm boyunca iki kenarından destekliyor; kutu içinde 4 vidayla tutulan PCB'nin rezonans frekansı çok daha düşük |
| 4 | **Hizalama** — kart kenarı konnektörünün ihtiyacı olan giriş açısı ve yükseklik garantisini kızak veriyor |

Draft'ın **kilit mandalı, kızak rayı ve önden tak-kilitle** yaklaşımı aynen
korunuyor — sadece node'un etrafındaki kutu kalkıyor.

**Fan ihtiyacı da düşüyor:** blade'de ısı doğrudan havaya geçtiği için gereken
debi 1.6 CFM'e iniyor (40 mm fanın %30 devri, ~0.2 W).
[04 §6.2](04-backplane-mekanik.md#62-gereken-hava-debisi-hesap)

---

## 4. Draft'ın doğrudan benimsenen kalemleri

Bunlar tartışmasız — draft zaten doğru çözmüş:

| Kalem | Not |
|-------|-----|
| **3 kademeli pin stagger** | GND uzun → Power orta → Signal kısa. [04 §5.1](04-backplane-mekanik.md#51-mate-sırasının-mantığı) ile birebir uyumlu. Draft'ta PRESENT/DETECT için 4. kademe yok — eklenmesi öneriliyor |
| **Mekanik kilit mandalı** | K5 (titreşim) için zorunlu, draft'ta zaten var |
| **Kızak rayı + yan kılavuz** | Önden tak-kilitle-kullan; servis gereksinimini karşılıyor |
| **DETECT / FAULT / RST / BST hatları** | Mimarideki PRESENT# / FAULT# / MOD_RST# / BOOT# ile birebir örtüşüyor — bağımsız olarak aynı sonuca varılmış |
| **Node ölçüleri** | 17.5 / 35 × 80 × 110 mm — varsayım yerine gerçek ölçü |
| **3D baskı + alüminyum hibrit** | Prototip için doğru; alüminyum ray ayrıca ısı yolu olabilir (§3.5) |

---

## 5. Revize edilmesi gereken dokümanlar

| Doküman | Gerekçe |
|---------|---------|
| [04](04-backplane-mekanik.md) | ✅ **Baştan yazıldı** — blade mimarisi, 17.5 mm, kızak sistemi, hava akışı |
| [09](09-node-aileleri.md) | Klemens/kanal sayısı 17.5 mm'ye göre; iki sıra klemens |
| [11](11-cikis-node-topolojileri.md) | **Termal hesap düzeltilmeli** (§3.5); kanal sayıları revize |
| [10](10-enerji-butcesi.md) | Fan enerji kalemi eklenmeli (D-57) |
| [03](03-guc-mimarisi.md) | Fan beslemesi; 3.3V rail rezervasyonu |
| Tümü | Terminoloji Host/Node (D-56 onayına bağlı) |

Bu revizyonlar, çakışma kararları (§2 tablosu) netleştikten sonra tek seferde
yapılacak — parça parça değil.
