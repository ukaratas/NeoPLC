# 05 — Dahili Bus

Host ile node'lar arasındaki haberleşme. Hedef: **düşük sınıf MCU'da rahat
çalışan, kolay debug edilen, uzun vadede sürdürülebilir** bir bus.

---

## 1. Fiziksel katman kararı

Brief'in en çok gerekçe istediği nokta: "UART tabanlı" ifadesi çıplak TTL-UART'a
kilitlenmemeli.

### 1.1 TTL UART neden yetmiyor

Ortam: 8U backplane, 9 düğüm (host + 8 node), her node'da kendi anahtarlamalı
regülatörü, hot-plug ihtimali, endüstriyel EMI.

| Sorun | Açıklama |
|-------|----------|
| **Ground bounce doğrudan sinyale biniyor** | 3.3V CMOS'ta V_IL(max) = 0.8V. Node'ların darbeli akım çekişi slotlar arası birkaç yüz mV GND farkı yaratır — gürültü marjının önemli kısmı daha başlamadan gidiyor. **Belirleyici sorun budur.** |
| Multi-drop open-drain zorunluluğu | Çakışmayı önlemek için open-drain + pull-up gerekir → yavaş kenarlar, sürekli pull-up akımı, hız tavanı |
| Hot-plug kilitlenmesi | Beslemesiz node takıldığında ESD diyotları busu GND'ye kelepçeler → tüm bus düşer |
| Tanımsız idle | Hiçbir sürücü aktif değilken hat serbest — çerçeve senkronizasyonu güvenilmez |

### 1.2 RS-485 ne getiriyor

| Özellik | Kazanç |
|---------|--------|
| **±7V common-mode reddi** | Slotlar arası ground bounce'a **tamamen bağışık**. Asıl kazanç bu — §1.1'in belirleyici sorununu doğrudan çözüyor. |
| Multi-drop için tasarlanmış | 32+ düğüm, fail-safe bias ile tanımlı idle durumu |
| Hot-plug toleranslı varyantlar | "Glitch-free power-up/down" transceiver'lar standart |
| Slew-rate sınırlı varyantlar | EMI belirgin şekilde düşüyor |

### 1.3 Maliyet ve güç itirazının gerçek büyüklüğü

Brief "düşük güç tüketimli" diyor. İtirazı sayıyla test edelim:

```
Transceiver birim fiyatı (LCSC sınıfı)  ≈  $0.15 – 0.35
Alıcı sürekli açık tüketimi              ≈  0.5 mA @ 3.3V  =  1.65 mW
8 node toplam                           ≈  13 mW
```

Karşılaştırma: tek bir Cortex-M0+ MCU 64MHz'de ~10 mA @3.3V = **33 mW.**

**Sonuç: 8 transceiver'ın toplam tüketimi, tek bir node MCU'sunun yarısı kadar.
Düşük güç argümanı TTL lehine çalışmıyor.**

> Not: Transceiver'ın shutdown moduna alınması düşünülemez — node'un host'u
> her an duyabilmesi gerekiyor. Alıcı sürekli açık kalmalı.

### Karar: RS-485 diferansiyel

Yazılım protokolü UART kadar basit kalıyor ([§6](#6-çerçeve-formatı)); sadece
fiziksel taşıma katmanı sağlamlaştırılıyor. Brief'in istediği ayrım tam olarak
bu.

### 1.4 CAN alternatifi

Dürüstlük gereği değerlendirildi:

| Artı | Eksi |
|------|------|
| Donanımsal arbitrasyon | Node'da CAN kontrolcüsü gerekir → MCU seçimini daraltır ve pahalılaştırır |
| Donanımsal ACK ve hata sayaçları | Klasik CAN'de 8 byte çerçeve sınırı |
| Polling'siz event-driven bildirim | Protokol ağırlığı — "UART kadar basit" hedefiyle çelişiyor |

**Karar: RS-485.** CAN, ileride çok-host veya gerçek event-driven ihtiyacı
doğarsa yükseltme yolu olarak korunuyor — **backplane'deki A/B çifti CAN'e de
uygun, sadece transceiver değişir.** Pinout bu yüzden geleceğe dayanıklı.

Ayrıca event-driven ihtiyacı pratikte zayıf: node kendi gerçek zamanlı
korumasını yapıyor, host'un öğrenmesi 100 ms gecikebilir — CAN'in bu
avantajının bu uygulamada karşılığı yok.

---

## 2. Yarım dupleks mi tam dupleks mi?

| | Yarım dupleks (2 tel) | Tam dupleks (4 tel) |
|---|---|---|
| Backplane pini | 2 | 4 |
| Transceiver maliyeti | ~$0.15 | ~$0.40 |
| LCSC seçenek zenginliği | **Çok yüksek** | Orta |
| Turnaround riski | Var — donanım DE ile yönetilir | Yok |
| Arızalı node izolasyonu | Her iki yön de etkilenebilir | Host→node yönü korunur |

200 mm'lik bir bus için turnaround gerçek bir problem değil: hem ESP32 hem STM32
USART'ları **donanımsal DE kontrolü** sunuyor, yazılım gecikmesi devre dışı.

### Karar: yarım dupleks 2 tel

**Ancak pinout'ta tam dupleks için 2 pin rezerve ediliyor**
([04 §5](04-backplane-mekanik.md#5-pinout), pin 15–16). Pinout geri dönülemez
olduğu için bu rezervasyon şimdi yapılmalı — maliyeti sıfır, atlanmasının
maliyeti tüm node ailesi.

---

## 3. Sonlandırma analizi

Sonlandırma gerekli mi? Hesapla:

```
Backplane elektriksel uzunluk        ≈  200 mm
FR4'te yayılım hızı                  ≈  0.15 m/ns
t_prop                               =  0.200 / 0.15  =  1.33 ns

Slew-rate sınırlı transceiver t_r    ≈  200 – 400 ns
Lumped devre kriteri                 :  t_prop < t_r / 6
                                        1.33 ns  <<  33 – 67 ns   ✓ 25–50× marj
```

### Karar: yansıma sonlandırması yok

Hat elektriksel olarak **toplu (lumped) devre** — yansıma diye bir olgu yok.

**Bu doğrudan güç kazancı:** İki uçta 120Ω sonlandırma, sürücüye 60Ω DC yük
demek — sürekli ~25 mA. Brief'in düşük güç hedefi göz önüne alındığında bunu
harcamak gereksiz.

### 3.1 Fail-safe bias — bu gerekli

Sonlandırma gereksiz, **bias gerekli.** Hiçbir sürücü aktif değilken diferansiyel
hat tanımsız kalır; alıcı gürültüyü veri sanabilir.

```
Host ucunda:
  BUS_A → pull-up  (+3.3V)
  BUS_B → pull-down (GND)
  → idle durumda V_AB > +200 mV garanti edilir (mark/idle seviyesi)
```

Bias dirençleri host'ta **tek noktada** bulunur — node'larda bias yoktur.
Node sayısı değiştikçe bias noktası değişmez.

---

## 4. Hız ve tarama süresi

```
500 kbaud, 8N1  →  10 bit/byte  →  20 µs/byte

Bir node işlemi (EXCHANGE):
    istek       8 byte   =  160 µs
    turnaround           ≈   80 µs
    yanıt      16 byte   =  320 µs
    slot arası boşluk    ≈   40 µs
                           ───────
                           ~600 µs

8 node tam tarama      =  4.8 ms   →  ~200 Hz tarama frekansı
```

| Referans | Değer |
|-----------|-------|
| NeoPLC tarama süresi | 4.8 ms |
| Tipik endüstriyel PLC tarama | 10 – 100 ms |
| **Marj** | **2 – 20×** |

> ⚠️ **200 Hz terk edildi.** Bu hesap teknik kapasiteyi gösteriyor, çalışma
> noktasını değil. Enerji bütçesi ([10 §2.1](10-enerji-butcesi.md#21-tarama-hızı-gerçekte-ne-olmalı))
> tarama hızını **uyarlanabilir 20 / 10 / 1 Hz**'e indirdi — 200 Hz node'ların
> uyumasını engelliyordu ve karavan yükleri için 20× gereksizdi.
>
> Yüksek baud hızı yine de değerli: **çerçeve ne kadar kısa sürerse node o
> kadar az uyanık kalıyor.** 500 kbaud'da bir işlem 600 µs; 115200'de 2.6 ms.
> 10 Hz taramada bu %0.6 vs %2.6 duty cycle demek — **4× enerji farkı.**

### Karar: 500 kbaud

**Hız için değil, denge için seçildi.** 115200 baud bile 20 ms tarama ile
yeterdi. 500k'nın seçilme sebebi:

- Slew-rate sınırlı transceiver'larla uyumlu (EMI düşük kalıyor)
- Tarama marjı, ESP32'nin WiFi kaynaklı jitter'ı için tampon oluşturuyor
  ([02 §1](02-host-mimarisi.md#dürüst-karşı-argümanlar))
- Firmware güncellemesinde blok transferi makul sürede bitiyor

Baud hızı konfigüre edilebilir olacak — saha koşullarına göre düşürülebilmeli.

---

## 5. Trafik modeli

### Karar: katı host-node + donanım event hattı

| Kural | Sonuç |
|-------|-------|
| **Node asla kendiliğinden konuşmaz** | Çakışma yok, arbitrasyon yok, tamamen deterministik |
| **Node işlemler arasında uyur** | STOP modunda ~2 µA, USART start-bit ile uyanır ([10 §3](10-enerji-butcesi.md#3-wake-on-bus-nodeların-uyuması)) |
| Host sırayla slot 0..7 tarar | Tarama süresi sabit ve öngörülebilir |
| Node yanıt süresi ≤ 500 µs | Aşılırsa host devam eder, gecikme birikmez |
| Host timeout 2 ms | Kaybolan node taramayı kilitlemiyor |
| **Arızalar poll ile toplanır** | Node arızayı **latch'ler**, host bir sonraki taramada okur — en fazla 100 ms gecikme |

**FAULT# donanım hattı kaldırıldı.** Gerekçe: 10 Hz taramada olay gecikmesi en
fazla 100 ms, ve gerçek zamanlı koruma zaten node'un kendi işi (kısa devre için
100 ms de çok geç). Ek kazanç: wired-OR hattın bir arıza modu vardı — hattı
düşük tutan tek arızalı node diğerlerinin arızasını maskeliyordu; o mod da
ortadan kalktı. Tam gerekçe:
[04 §5.3](04-backplane-mekanik.md#53-neden-26-değil-12-kaldırılanların-gerekçesi)

> **Node arızayı latch'lemeli** — iki poll arasında oluşan olay kaybolmamalı.

---

## 6. Çerçeve formatı

### Karar

```
┌────────┬──────┬──────┬─────┬─────────────────┬────────┐
│ SYNC   │ ADDR │ FUNC │ LEN │ PAYLOAD 0..64   │ CRC16  │
│ 0x55   │  1   │  1   │  1  │                 │   2    │
└────────┴──────┴──────┴─────┴─────────────────┴────────┘
   1        1      1      1        0..64            2      = max 70 byte
```

| Alan | Açıklama |
|------|----------|
| SYNC | 0x55 — alternating bit paterni, senkronizasyon ve baud doğrulama için ideal |
| ADDR | bit7 = yön (0 = host isteği, 1 = node yanıtı) · bit6..0 = adres |
| | 0x00 = broadcast · **0x7E = adressiz node** (enumerasyon) · 0x7F = rezerve |
| FUNC | İşlem kodu (§7) |
| LEN | Payload uzunluğu |
| CRC16 | CRC-16/MODBUS — kanıtlanmış, tablosuz da hesaplanabilir |

### 6.1 Neden Modbus RTU'nun sessizlik çerçevelemesi kullanılmıyor

Modbus RTU çerçeveleri **3.5 karakterlik sessizlikle** ayırır. Bu:

- Düşük sınıf MCU'da hassas timer bağımlılığı yaratır
- Debug'ı zorlaştırır (logic analyzer'da çerçeve sınırı görünmez)
- Baud değiştiğinde timing yeniden ayarlanmalıdır

**LEN + CRC ile açık çerçeveleme** bu üç sorunu da ortadan kaldırıyor. Brief'in
"kolay debug edilebilen" hedefine doğrudan hizmet ediyor.

---

## 7. Fonksiyon kodları

| Kod | İşlem | Kullanım |
|-----|-------|----------|
| 0x01 | IDENTIFY | Node descriptor'ını oku |
| 0x02 | GET_STATUS | Sağlık özeti |
| 0x03 | READ_INPUTS | Giriş proses imajı |
| 0x04 | WRITE_OUTPUTS | Çıkış proses imajı |
| **0x05** | **EXCHANGE** | **Çıkışları yaz + girişleri oku, tek round-trip** |
| 0x06 | READ_CONFIG | Konfigürasyon oku |
| 0x07 | WRITE_CONFIG | Konfigürasyon yaz |
| 0x08 | GET_DIAG | Detaylı arıza bilgisi |
| **0x0E** | **SET_ADDRESS** | **Adressiz node'a kısa adres ata** (enumerasyon) |
| **0x0F** | **SYNC (broadcast)** | **Tüm node'lar aynı anda latch/apply** — SYNC pini yerine |
| **0x0E** | **SET_ADDRESS** | **Adressiz node'a kısa adres ata** — enumerasyon ([06 §1](06-slot-yonetimi.md#1-slot-adresleme)) |
| **0x0F** | **SYNC (broadcast)** | **Tüm node'lar aynı anda latch/apply** — SYNC pini yerine |
| 0x10 | ENABLE | Node'u çalıştır |
| 0x11 | DISABLE | Node'u durdur (çıkışlar güvenli duruma) |
| 0x20–0x2F | Firmware update | ERASE / WRITE_BLOCK / VERIFY / ACTIVATE — [07](07-firmware-update.md) |
| 0x7F | RESET | Yazılımsal reset |

**Normal tarama döngüsü yalnızca 0x05 EXCHANGE kullanır** — node başına tek
işlem. Diğer kodlar discovery, konfigürasyon ve bakım içindir; tarama süresine
girmezler.

### 7.1 Node descriptor'ı (IDENTIFY yanıtı)

| Alan | Byte | Not |
|------|------|-----|
| **Protokol versiyonu** | 1 | **İlk bayt — geriye uyumluluğun tek kapısı** |
| Node tipi ID | 2 | 0x0101 = DI, 0x0201 = DO, 0x0301 = AI, ... |
| Vendor ID | 2 | Üçüncü parti node'lar için |
| HW revizyonu | 1 | |
| FW versiyonu | 3 | major.minor.patch |
| Form faktör | 1 | 1U / 2U |
| Giriş kanal sayısı | 1 | |
| Çıkış kanal sayısı | 1 | |
| Yetenek bayrakları | 4 | |
| Benzersiz kimlik | 12 | MCU fabrika UID'si |
| **Beyan edilen sürekli tüketim** | 2 | **mA @5V — bütçe zorlaması için** |
| **Beyan edilen tepe darbe akımı** | 2 | **mA @5V — toplu işlem zamanlaması için** ([03 §5.5](03-guc-mimarisi.md#55-descriptora-eklenen-alan)) |
| CRC | 2 | |
| **Toplam** | **34 byte** | |

İki alan özellikle kritik:

- **Protokol versiyonu:** Host tanımadığı versiyonu görürse node'u devre dışı
  bırakır ama rafı düşürmez. Sözleşmeyi ileride kontrollü kırabilmenin tek yolu.
- **Beyan edilen güç:** Host, bütçe aşılıyorsa node'un reset'ini bırakmıyor
  ([03 §4.4](03-guc-mimarisi.md#44-güç-bütçesi-zorlaması)). Güç bütçesi kâğıt
  üzerinde kalmıyor, donanımla zorlanıyor.

---

## 8. Zamanlama disiplini

```
Host:
  ├─ slot 0 EXCHANGE ─┐
  │                   ├─ yanıt ≤ 500 µs, timeout 2 ms
  ├─ slot 1 EXCHANGE ─┘
  ├─ ...
  ├─ slot 7 EXCHANGE
  ├─ SYNC darbesi  ←── tüm node'lar aynı anda latch/apply
  └─ döngü başa
```

| Olay | Davranış |
|------|----------|
| Node yanıt vermedi | Timeout, hata sayacı artar, tarama devam eder |
| 3 ardışık timeout | Node "kayıp" işaretlenir, Modbus durum bitine yansır |
| CRC hatası | Yanıt atılır, sayaç artar, bir sonraki döngüde tekrar denenir |
| Node arıza bayrağı bildirdi | Tarama döngüsü sonunda GET_DIAG ile ayrıntı alınır |
| PRESENT# değişti | PCA9555 INT# → discovery tetiklenir |
| Tarama hızı değişti | Host broadcast ile bildirir; node'lar uyku pencerelerini ayarlar |

---

## 9. SYNC — donanım pini değil, broadcast çerçeve

### Karar: 0x0F SYNC broadcast · D-21 (revize)

Host bir broadcast çerçeve gönderir → **tüm node'lar girişlerini aynı anda
latch'ler, çıkışlarını aynı anda uygular.**

**Neden ayrı bir pin gerekmiyor:** Bus zaten broadcast. Bir çerçeve tüm
node'lara aynı anda ulaşıyor.

```
Donanım strobe eşzamanlılığı   ~ns
Broadcast çerçeve              ~µs    (çerçeve alım jitter'ı)
Karavan yüklerinin ihtiyacı    ~ms
```

µs ile ns arasındaki fark bu uygulamada ölçülemez. **1 pin yerine 1 fonksiyon
kodu** — SYNC pini pinout'tan kaldırıldı
([04 §5.3](04-backplane-mekanik.md#53-neden-26-değil-12-kaldırılanların-gerekçesi)).

### 9.1 Kullanım kuralı — röleler SYNC ile uygulanmaz

| Çıkış tipi | Uygulama anı | Gerekçe |
|------------|--------------|---------|
| MOSFET | **Broadcast SYNC** | Akım basamağı yok, eşzamanlılık bedava |
| **Latching röle** | **Node'un kendi işlemi sırasında** | Bobin darbeleri eşzamanlı olmamalı — host'un sıralı taraması doğal olarak ~600 µs arayla dağıtıyor |
| Girişler (tüm tipler) | Broadcast SYNC | Örnekleme skew'i ortadan kalkıyor |

Röleleri SYNC'e bağlamak, 8 node'un bobinini aynı anda ateşleyip rayda 560 mA
sıçrama yaratırdı. Sıralı uygulama ile rafta aynı anda **tek bobin** enerjili
oluyor. Ayrıntı: [03 §5.4](03-guc-mimarisi.md#54-karar-sıralama-mimaride-kapasitör-kenarda)

### 9.2 Neden hâlâ değerli

SYNC olmadan slot 1'in girişi ile slot 8'in girişi arasında bir tam tarama
süresi (4.8 ms) fark olur. Broadcast SYNC ile tüm proses imajı **tek bir zaman
anına** ait oluyor — maliyeti sıfır.
