# 06 — Slot Yönetimi

Adresleme, discovery, presence/fault/reset mantığı ve güç bütçesi zorlaması.

---

## 1. Slot adresleme

### Karar: host adres atar — ADDR pinleri yok · D-17 (revize)

| Yöntem | Pin | Değerlendirme |
|--------|-----|---------------|
| Coğrafi (backplane'de sabit ADDR pinleri) | **4** | Stateless ve anında, ama node'un konumunu bilmesini gerektiriyor |
| **Host atamalı, RST# ile izole enumerasyon** | **0** | **Seçilen** — node konumdan habersiz kalıyor |
| Enumerasyon, seçici mekanizma olmadan | 0 | Çakışma riski — birden fazla node aynı anda cevap verir |

**Anahtar gözlem:** Host'ta zaten **slot başına MOD_RST#** var. Bu, çakışmasız
enumerasyon için gereken seçici mekanizmanın ta kendisi — ayrıca adres pini
gerekmiyor.

### 1.1 Enumerasyon akışı

```
1. Host tüm node'ları reset'te tutar        (MOD_RST# varsayılan aktif — §6)
2. Slot N'in RST#'ini bırakır               → bus'ta TEK node uyanık
3. Host 0x7E (adressiz) adresine IDENTIFY gönderir
4. Node descriptor'ını döner (UID dahil)
5. Host 0x0E SET_ADDRESS ile kısa adres = N atar
6. Sıradaki slota geçer
```

**Çakışma imkânsız**, çünkü adım 2–5 boyunca yalnızca bir node uyanık.

```
Açılış süresi = 8 × (node boot ~30 ms + handshake ~5 ms)  ≈  300 ms
```

### 1.2 Neden node'un konumu bilmemesi daha iyi

| | Coğrafi | Host atamalı |
|---|---|---|
| Node firmware'i | ADDR pinlerini okumalı | **Konum kavramı hiç yok** |
| Aynı node farklı slotta | Adresi değişir | Davranışı birebir aynı |
| Backplane | Slot başına 4 sabit bağlantı | Yok |
| Pin maliyeti | **4 pin** | **0** |

Host zaten hangi slotta ne olduğunu biliyor — bilmesi gereken taraf o. Node'un
kendi konumunu bilmesinin hiçbir işlevsel karşılığı yoktu.

### 1.3 Kaybedilen ve telafisi

| Kayıp | Telafi |
|-------|--------|
| Anında adres (enumerasyon yok) | ~300 ms açılış — kabul edilebilir |
| Node reset olursa adresini kaybeder | Node "adressiz" bayrağıyla cevap verir; host o slotu RST# ile izole edip yeniden atar |
| Host reset olursa tüm adresler gider | Host zaten baştan enumerasyon yapıyor |

**Adres ataması RAM'de tutulur, kalıcı yazılmaz** — böylece bir node başka bir
sisteme takıldığında eski adresi taşımaz.

## 2. Naif tasarımın problemi

8 slotu doğrudan MCU'ya bağlamak:

```
8 × PRESENT#  +  8 × FAULT#  +  8 × RESET#  +  8 × BOOT#  =  32 GPIO
```

ESP32-S3-WROOM'da ~30 kullanılabilir GPIO var — sadece slot yönetimi tüm bütçeyi
yiyor, Ethernet ve bus'a yer kalmıyor.

---

## 3. Host tarafı I/O genişletme

### Karar: üç katmanlı çözüm — 32 sinyal → 4 GPIO

#### Katman 1 — PRESENT# ve MOD_RST# → tek PCA9555

```
PCA9555 (I²C, 16-bit)
  Port 0 (giriş)   :  8 × PRESENT#
  Port 1 (çıkış)   :  8 × MOD_RST#
  INT# pini        :  presence değişiminde tetiklenir
```

**INT# pini kritik:** Hot-plug algılaması polling'siz, kesme ile geliyor. Node
takıldığı anda host haberdar oluyor.

Maliyet: 2 GPIO (I²C) + 1 GPIO (INT#) = **3 GPIO, 16 sinyal.**

#### Katman 2 — FAULT# ve BOOT# hatları tamamen kaldırıldı

İlk taslakta ortak wired-OR FAULT# ve ortak BOOT# hatları vardı. İkisi de
gereksiz çıktı:

- **FAULT#** → arızalar poll ile toplanıyor (§4)
- **BOOT#** → bootloader penceresi ile çözülüyor (§5)

### Sonuç

| | Naif | Şimdiki |
|---|---|---|
| MCU GPIO | 32 | **3** (I²C + INT#) |
| Backplane hattı / slot | 4 | **2** (PRESENT#, MOD_RST#) |
| Ortak backplane hattı | 0 | **0** |

PCA9555 tek başına 8 presence girişi + 8 reset çıkışını taşıyor; başka hiçbir
slot sinyali kalmadı.

---

## 4. Arıza bildirimi

### Karar: donanım hattı yok, poll ile · D-20 (revize)

```
Node arızayı tespit eder  →  kendi kanalını KORUR (µs mertebesinde)
                          →  arıza bayrağını LATCH'LER
Host bir sonraki taramada okur  →  en fazla 100 ms gecikme (10 Hz)
```

**Neden FAULT# donanım hattı kaldırıldı:**

| Gerekçe | Detay |
|---------|-------|
| Gecikme önemsiz | 10 Hz taramada en fazla 100 ms. Kayıt ve uyarı için fazlasıyla yeterli |
| **Gerçek zamanlı koruma zaten node'un işi** | Kısa devre için 100 ms de çok geç — node µs'ler içinde kendi kanalını kapatmak zorunda. Host'un rolü haber almak, müdahale etmek değil |
| **Wired-OR'un bir arıza modu vardı** | Hattı düşük tutan tek arızalı node, diğer tüm node'ların arızasını maskeliyordu. Bu mod da ortadan kalktı |

> **Zorunlu:** Node arıza durumunu **latch'lemeli**. İki poll arasında oluşan ve
> kendiliğinden geçen bir olay kaybolmamalı. `GET_STATUS` okunduğunda bayrak
> temizlenir.

### 4.1 S2'de gecikme

Bekleme durumunda tarama 1 Hz'e iner → arıza gecikmesi 1 saniyeye çıkar. Kabul
edilebilir: S2'de zaten aktif yük yok ([10 §4](10-enerji-butcesi.md#4-güç-durumları)).

## 5. Bootloader'a giriş

### Karar: donanım hattı yok, bootloader penceresi · D-19 (revize)

```
1. Host o slotun MOD_RST#'ini çeker      →  uygulama durur
2. RST# bırakılır                        →  bootloader çalışıyor, uygulama HENÜZ değil
3. Bootloader ~30 ms bus'ı dinler
4. Host "bootloader'da kal" çerçevesi gönderir
5. Gelmezse bootloader uygulamaya atlar
```

**Kilitlenmiş uygulama bu pencerede çalışmıyor**, dolayısıyla engel olamaz —
BOOT# hattının çözdüğü problem, per-slot RST# ile zaten çözülmüş durumda.

Bus'ı meşgul eden başka bir node varsa host onu da RST# ile susturabilir. Yani
host her koşulda hedef node ile baş başa kalabiliyor.

| | BOOT# hattı | Bootloader penceresi |
|---|---|---|
| Backplane pini | 1 (ortak) | **0** |
| Kilitlenmiş app'ten kurtarma | ✓ | ✓ |
| Bedeli | 1 pin | Her açılışta ~30 ms |

Açılışlar nadir; 30 ms bedel pratikte görünmez.

## 6. Reset varsayılan durumu

### Karar: node'da 10k pull-**down** → varsayılan reset'te

```
MOD_RST#  ──10k──  GND        (node üzerinde)
    │
    └── Host PCA9555 Port1 çıkışı
```

**PCA9555 güç açılışında tüm pinleri giriş (yüksek-Z) yapar.** Pull-down
sayesinde bu durumda node **reset'te tutulur.**

### 6.1 Bunun sağladığı güvenlik özelliği

```
Node takılır
   ↓
MCU reset'te — µA mertebesinde çekiyor
   ↓
Host PRESENT# görür → IDENTIFY gönderir
   ↓
Descriptor'daki "beyan edilen güç tüketimi" okunur
   ↓
┌─────────────────────────────┬──────────────────────────────┐
│ Bütçe yeterli               │ Bütçe aşılıyor               │
│   → MOD_RST# bırakılır      │   → MOD_RST# bırakılmaz      │
│   → node çalışır           │   → node reset'te kalır     │
│                             │   → Modbus'ta hata bildirilir│
└─────────────────────────────┴──────────────────────────────┘
```

**Güç bütçesi donanımla zorlanıyor.** Bir kullanıcı rafı aşırı doldurursa sistem
çökmüyor — fazla node basitçe devreye alınmıyor ve durum raporlanıyor.

Pull-**up** seçseydik node'lar host hazır olmadan çalışmaya başlardı ve bu
koruma mümkün olmazdı. Tek direncin yönü, bir sistem özelliğini belirliyor.

### 6.2 İkinci işlev: S3 depo modu

Bu mekanizma sonradan ikinci bir amaca hizmet etti: **S3 depo modunda tüm
node'lar reset'te tutularak µA seviyesine indiriliyor**
([10 §4.1](10-enerji-butcesi.md#41-s3-mevcut-kararların-beklenmedik-yakınsaması)).

Güç bütçesi zorlaması için tasarlanan pull-down, batarya ömrünün de mekanizması
oldu. Ek donanım gerekmedi.

> **Not:** Node'un reset'te µA çekmesi, MCU reset pininin gerçekten MCU'yu
> reset'te tutmasına bağlı. Node tasarımında MOD_RST#'in doğrudan MCU NRST'ye
> (veya bir enable hattına) gitmesi gerekiyor.

---

## 7. Slot başına akım koruması

### Karar: akım sınırlı load switch (+5V_SYS üzerinde)

Maliyet: ~$0.20 × 8 = **$1.60** host başına.

Üç işi birden yapıyor:

| İşlev | Kazanç |
|-------|--------|
| **Arıza izolasyonu** | Kısa devre yapan bir node tüm rafı düşürmüyor |
| **Soft-start** | Hot-plug inrush'ı sınırlıyor — komşu slotların rail'i çökmüyor |
| **Arıza tespiti** | Aşırı akım durumu host'a bildiriliyor |
| **S3 depo modu** | Node'ları **tamamen** beslemeden keser — µA değil, sıfır ([10 §4.1](10-enerji-butcesi.md#41-s3-mevcut-kararların-beklenmedik-yakınsaması)) |

**Ucuz alternatif:** slot başına polyfuse (~$0.05). Ama yavaş, soft-start
vermiyor ve arıza bildirimi yok. $1.15 fark için üç işlevi birden kaybetmek
mantıklı değil.

Bu karar [04 §8](04-backplane-mekanik.md#8-hot-plug-değerlendirmesi)'teki
hot-plug maliyetini de karşılıyor — load switch zaten gerekliydi.

---

## 8. Discovery akışı

### Karar

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PCA9555 INT#  →  presence bitmap değişti                 │
├─────────────────────────────────────────────────────────────┤
│ 1b. Slot N'in RST#'i bırakılır → bus'ta tek node uyanık      │
│     IDENTIFY(0x7E) → descriptor · SET_ADDRESS(N)            │
├─────────────────────────────────────────────────────────────┤
│ 2. IDENTIFY(N)  →  32 byte descriptor doğrulama             │
├─────────────────────────────────────────────────────────────┤
│ 3. Doğrulama:                                               │
│      · CRC                                                  │
│      · Protokol versiyonu tanınıyor mu?                     │
│      · Güç bütçesi yeterli mi?                              │
│      · 2U ise N+1 boş mu?                                   │
├─────────────────────────────────────────────────────────────┤
│ 4. WRITE_CONFIG  →  kanal konfigürasyonu                    │
├─────────────────────────────────────────────────────────────┤
│ 5. ENABLE  →  node tarama döngüsüne alınır                 │
└─────────────────────────────────────────────────────────────┘
```

### 8.1 Doğrulama başarısız olursa

| Durum | Davranış |
|-------|----------|
| CRC hatası | 3 kez tekrar, sonra "hatalı node" işaretle |
| Bilinmeyen protokol versiyonu | Node devre dışı, **raf çalışmaya devam eder** |
| Güç bütçesi aşımı | Reset bırakılmaz, Modbus'ta bildirilir |
| 2U ama N+1 dolu | Konfigürasyon hatası olarak bildirilir |

**Hiçbir başarısızlık durumu rafı düşürmüyor.** Tek bir arızalı veya uyumsuz
node, çalışan sistemi etkilemiyor — bir platform ürünü için temel gereksinim.

### 8.2 Node'un kaybolması

```
PRESENT# yükseldi  →  node çıkarıldı
   ↓
Host node'u tarama döngüsünden çıkarır
Güç bütçesi tahsisi serbest bırakılır
Modbus slot doluluk haritası güncellenir
Slot'un MOD_RST#'i tekrar aktif edilir (bir sonraki node için hazır)
```

---

## 9. Slot durum makinesi

```
        ┌──────────┐
        │  EMPTY   │ ←──────────────────────┐
        └────┬─────┘                        │
             │ PRESENT# düştü               │ PRESENT# yükseldi
             ▼                              │ (her durumdan)
        ┌──────────┐                        │
        │ DETECTED │ ── reset'te tutuluyor  │
        └────┬─────┘                        │
             │ IDENTIFY başarılı            │
             ▼                              │
        ┌──────────┐                        │
        │IDENTIFIED│                        │
        └────┬─────┘                        │
             │ bütçe + versiyon OK          │
             ▼                              │
        ┌──────────┐                        │
        │CONFIGURED│                        │
        └────┬─────┘                        │
             │ ENABLE                       │
             ▼                              │
        ┌──────────┐    arıza / timeout     │
        │  ACTIVE  │ ──────────────┐        │
        └──────────┘               ▼        │
                              ┌────────┐    │
                              │ FAULTED│ ───┘
                              └────────┘
```

| Durum | Anlam | MOD_RST# |
|-------|-------|----------|
| EMPTY | Slot boş veya 2U tarafından kapatılmış | aktif (düşük) |
| DETECTED | Fiziksel olarak takılı, henüz tanınmadı | aktif |
| IDENTIFIED | Descriptor okundu, doğrulanıyor | aktif |
| CONFIGURED | Doğrulandı, konfigüre edildi | bırakıldı |
| ACTIVE | Tarama döngüsünde | bırakıldı |
| FAULTED | Arıza bildirdi veya yanıt vermiyor | duruma göre |
