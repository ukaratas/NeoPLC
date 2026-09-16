# 09 — Modül Aileleri

---

## 1. Ortak modül çekirdeği

Platformun en önemli tasarım kalemi. Her modül, **aynı değişmez çekirdeği**
paylaşır; sadece saha tarafı farklıdır.

```
┌─────────────────────────────────────────────────────────────┐
│  MODÜL                                                      │
│                                                             │
│  ┌── ORTAK ÇEKİRDEK (tüm modüllerde aynı) ──────────────┐   │
│  │                                                       │   │
│  │  Kart kenarı konnektörü (26 pin)                     │   │
│  │  +5V_SYS → 3.3V regülatör                            │   │
│  │  RS-485 transceiver                                  │   │
│  │  MCU + protokol firmware'i                           │   │
│  │  ADDR0-3 pull-up'ları                                │   │
│  │  MOD_RST# pull-down                                  │   │
│  │  FAULT# open-drain sürücü                            │   │
│  │  SYNC girişi                                         │   │
│  │  BOOT# girişi                                        │   │
│  │  Soft-start                                          │   │
│  │  SWD test noktaları                                  │   │
│  └───────────────────────────────────────────────────────┘   │
│                            ↕                                 │
│  ┌── SAHA TARAFI (modül tipine özgü) ────────────────────┐   │
│  │  İzolasyon · sürücüler · filtreleme · klemensler      │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 Neden bu ayrım kritik

| Kazanç | Açıklama |
|--------|----------|
| **Yeni modül türetme maliyeti düşer** | Sadece saha tarafı tasarlanır; çekirdek kopyalanır |
| **Doğrulama bir kez yapılır** | Çekirdek bir modülde doğrulandıysa hepsinde doğrulanmıştır |
| **Firmware paylaşılır** | Protokol katmanı ortak kütüphane; modül sadece I/O katmanını yazar |
| **KiCAD'de yeniden kullanım** | Hiyerarşik sayfa veya design block olarak saklanabilir |

**Tasarım kuralı:** Çekirdekte yapılan her değişiklik tüm modül ailesini
etkiler. Çekirdek, ilk modülle birlikte donduruluyor.

### 1.2 Çekirdeğin BOM tahmini

| Bileşen | Tahmini |
|---------|---------|
| MCU (düşük sınıf, 32-bit) | ~$0.60 |
| RS-485 transceiver | ~$0.20 |
| 3.3V regülatör (5V→3.3V) | ~$0.15 |
| Pasifler, LED, soft-start | ~$0.30 |
| **Çekirdek toplamı** | **~$1.25** |

Kart kenarı konnektörü **$0** ([04 §2](04-backplane-mekanik.md#2-konnektör-seçimi)) —
bu, çekirdek maliyetinin neden bu kadar düşük kalabildiğinin ana sebebi.

---

## 2. İlk modül seçimi

### 🔴 D-28 — Karar bekliyor

**Öneri: Dijital giriş, 8 kanal, 1U.**

Gerekçe:

| Kriter | Dijital giriş |
|--------|---------------|
| Karmaşıklık | **En düşük** — optocoupler + seri direnç, başka bir şey yok |
| Saha koruması | Doğal olarak sağlam ([08 §1.1](08-emc-koruma.md#11-dijital-girişin-doğal-sağlamlığı)) |
| Çekirdek doğrulaması | **Tam** — backplane, protokol, discovery, güç, reset, fault mantığının hepsini kullanır |
| Güç tüketimi | En düşük — güç bütçesi varsayımlarını doğrulamak için iyi başlangıç |
| Hata riski | Saha tarafında yanlış gidecek çok az şey var |

**Amaç ilk modülde I/O fonksiyonunu göstermek değil, platform sözleşmesini
doğrulamaktır.** Bunun için en basit modül en iyisidir — saha tarafındaki
karmaşıklık, çekirdekteki sorunları maskeler.

### 2.1 Alternatif değerlendirmesi

| Aday | Neden ilk olarak uygun değil |
|------|------------------------------|
| Dijital çıkış | Yük sürme, freewheel, kısa devre koruması — çekirdek hatalarını maskeleyebilir |
| Röle çıkış | VBUS_RAW kullanımı ek değişken getirir; bobin akımı güç bütçesi testini bulandırır |
| Analog giriş | Referans, kalibrasyon, gürültü — en zor modül. Çekirdek olgunlaşmadan yapılmamalı |

---

## 3. Modül MCU'su

### ⚪ D-37 — Henüz ele alınmadı

Bu karar için gereken girdi:

| Girdi | Kaynak |
|-------|--------|
| Flash kapasitesi → bootloader yapısı | [07 §2](07-firmware-update.md#2-bootloader-yapısı) — 64 KB ise tek app, 128 KB+ ise çift bank yeniden değerlendirilir |
| GPIO sayısı | Modül tipine göre değişir; en yüksek kanal sayılı modül belirleyici |
| Donanımsal DE kontrolü olan USART | [05 §2](05-dahili-bus.md#2-yarım-dupleks-mi-tam-dupleks-mi) — turnaround gecikmesini yazılımdan çıkarmak için |
| Fabrika UID | [05 §7.1](05-dahili-bus.md#71-modül-descriptorı-identify-yanıtı) — descriptor'daki benzersiz kimlik |
| Sıcaklık sınıfı | D-04'e bağlı |
| LCSC stok ve fiyat | Konnect `integration` toolset'i ile doğrulanacak |

**Ön eğilim:** STM32G0 ailesi (G030/G031/G071) — düşük maliyet, donanımsal DE
kontrollü USART, geniş LCSC stoğu, endüstriyel sıcaklık aralığı, tek toolchain
ile tüm aile.

Karar, D-28 (ilk modül) netleştiğinde o modülün gereksinimleriyle birlikte
verilecek.

---

## 4. Saha bağlantısı

### ⚪ D-38 — Henüz ele alınmadı

22.5 mm ön yüz genişliğinde kaç kutup sığdığı, kanal sayısını doğrudan
sınırlıyor. Bu yüzden klemens seçimi bir mekanik karar değil, **kanal sayısı
kararıdır.**

| Seçenek | Adım | 22.5 mm'de | Not |
|---------|------|-----------|-----|
| Push-in yaylı klemens | 3.5 mm | ~6 kutup/sıra | Alet gerektirmez, endüstriyel standart |
| Vidalı klemens | 3.81 / 5.0 mm | ~5 / ~4 kutup/sıra | Yaygın, ucuz |
| Çıkarılabilir (pluggable) | 3.5 / 3.81 mm | ~6 / ~5 kutup/sıra | Servis kolaylığı, daha pahalı |

> ⚠️ **Titreşim (K5) vidalı klemensi eliyor.** Karavan hareketli bir araç;
> vidalı klemens titreşim altında gevşer ve gevşeyen bir klemens yüksek akımda
> ısınma ve yangın riskidir. **Push-in yaylı veya çıkarılabilir yaylı klemens
> zorunlu.** ([10 §9.3](10-enerji-butcesi.md#93-titreşim--🟡-d-45))

İki sıra kullanılırsa kutup sayısı ikiye katlanır (~12), ama ön yüz derinliği
artar.

**8 kanal + ortak dönüş = 9 kutup** gerektiriyor → iki sıra veya grup ortak
dönüş gerekli. Bu, D-28 ile birlikte kararlaştırılacak.

---

## 5. Modül ailesi yol haritası

| Faz | Aile | Form | Bağımlılık |
|-----|------|------|------------|
| **1** | Dijital giriş | 1U | Çekirdek doğrulaması — D-28 |
| **1** | Dijital çıkış | 1U | Çekirdek dondurulduktan sonra |
| **2** | Röle çıkış | 1U / 2U | VBUS_RAW kullanımının ilk doğrulaması |
| **2** | Analog giriş | 1U / 2U | Çekirdek olgun olmalı; gürültü bölgeleme kritik |
| **2** | Analog çıkış | 1U / 2U | VBUS_RAW compliance gerilimi |
| **3** | Haberleşme | 1U / 2U | Ek protokol yığını — modülde daha güçlü MCU gerekebilir |
| **3** | Özel fonksiyon | 1U / 2U | Sayaç, enkoder, PWM, sıcaklık (RTD/TC) |

### 5.1 Modül tipi ID tahsisi

Descriptor'daki `Modül tipi ID` alanı için ([05 §7.1](05-dahili-bus.md#71-modül-descriptorı-identify-yanıtı)):

```
0x01xx   Dijital giriş        0x0101 = 8ch 24V
0x02xx   Dijital çıkış        0x0201 = 8ch MOSFET
0x03xx   Analog giriş         0x0301 = 4ch 4-20mA · 0x0302 = 4ch 0-10V
0x04xx   Analog çıkış
0x05xx   Röle çıkış
0x06xx   Haberleşme
0x07xx   Özel fonksiyon
0xFFxx   Rezerve / test
```

Üst bayt aile, alt bayt varyant. Master, tanımadığı bir varyantı gördüğünde
aile davranışına göre genel muamele edebilir — yeni varyantlar master
güncellemesi gerektirmeden çalışabilir.

---

## 6. 1U → 2U türetme kuralı

Bir modülün 2U versiyonu **yeni bir tasarım değil, genişletilmiş bir
varyanttır**:

| Kalem | 1U | 2U |
|-------|----|----|
| Ortak çekirdek | Aynı | **Aynı** |
| Backplane konnektörü | 1 adet (sol slot) | **1 adet (sol slot)** — [04 §4](04-backplane-mekanik.md#4-2u-modül-stratejisi) |
| +5V_SYS bütçesi | 200 mA | 400 mA |
| Ön yüz genişliği | 22.5 mm | 45 mm |
| Kanal sayısı | Baz | Tipik 2× |
| Descriptor `form_factor` | 1U | 2U |

2U yalnızca şunlar için kullanılmalı: daha fazla saha bağlantısı, daha fazla
fiziksel alan gerektiren izolasyon/koruma, veya daha karmaşık fonksiyon.
**Sadece "daha rahat yerleşim" için 2U kullanılmamalı** — slot maliyeti yüksek.
