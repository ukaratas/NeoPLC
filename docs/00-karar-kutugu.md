# 00 — Karar Kütüğü

Tüm mimari kararların tek kaynağı. Bir karar burada 🟢 olmadan ilgili donanım
tasarlanmaz. Karar değişirse önce burası güncellenir.

**Son güncelleme:** 2026-09-17 · D-67 BLE v1

---

## Özet durum

| Durum | Adet |
|-------|------|
| 🟢 Kabul edildi | 71 |
| 🟡 Öneri hazır, onay bekliyor | 0 |
| 🔴 Dışarıdan bilgi gerekiyor | 0 |
| ⚪ Henüz ele alınmadı | 4 |
| ⛔ Superseded | 2 |

*Sayılar: D-67 ⚪→🟢 BLE uyandırma v1. Firmware kümesi ⚪ duruyor.*

---

## Kabul edilen kararlar

| ID | Karar | Kaynak |
|----|-------|--------|
| **D-01** | Host MCU: **ESP32-S3-WROOM-1U-N16R8** | Kullanıcı onayı |
| **D-02** | Ethernet kontrolcüsü W5500 — *kapsamı değişti:* **host'ta değil**, yalnız gelecekteki Ethernet haberleşme node'u için geçerli (D-47) | Kullanıcı onayı, D-47 ile yeniden kapsamlandırıldı |
| **D-04** | Hedef ortam sıcaklığı: **60 °C** | Kullanıcı — kapalı mekân, güneş altında 50 °C rahat görülür |
| **D-06** | EMC: **sertifikasyon hedefi yok**, seviye A (ESD + EFT) | Kullanıcı |
| **D-46** | Uygulama bağlamı: **karavan yönetimi**, batarya beslemeli | Kullanıcı |
| **D-47** | **Ethernet host kartından çıkarıldı** — RS-485 + WiFi yeterli | Kullanıcı onayı |
| **D-52** | **Çıkış: tek teknoloji / node.** MOSFET DO = **8ch 8A 1U**. 8A latching yok. Güç/AC kanalı 1U veya 2U — **4U yok** | Kullanıcı onayı (revize) |
| **D-56** | **Terminoloji: Host / Node** — tüm dokümanlarda uygulandı | Kullanıcı onayı |
| **D-05** | **Host 2 katman** — üç gerekçe de ortadan kalktı | Türetilmiş |
| **D-58** | **Slot adımı 17.5 mm** (2U = 35 mm) | Çalışma draftı Rev 0.1 |
| **D-60** | **Gerçek blade mimarisi** — şasi + kızak, kutu-içinde-kutu terk edildi | Kullanıcı |
| **D-65** | **WiFi varsayılan kapalı, talep üzerine açılır** | Kullanıcı |
| **D-66** | **Host = 2U blade, kendi özel slotunda** | Kullanıcı |
| **D-32** | **Backplane 26 → 12 pin** | Kullanıcı sorgusu üzerine uçtan uca değerlendirme |
| **D-08** | **Tek ray: sadece +5V** (VBUS_RAW kaldırıldı) | Aynı değerlendirme |
| **D-17** | **Adres pinleri yok, host atıyor** | Aynı değerlendirme |
| **D-19 / D-20 / D-21** | **BOOT# / FAULT# / SYNC pinleri kaldırıldı** | Aynı değerlendirme |
| **D-28** | **İlk node: DI-8** — 8ch 1U, 5–30 V izole | Kullanıcı onayı |
| **D-76** | **DI saha ~5–30 V izole** — 12 V ve 24 V aynı kart | Kullanıcı onayı |
| **D-37** | **Node MCU: STM32G071 128 KB, tüm node'lar aynı SKU** | Kullanıcı onayı |
| **D-38** | **Klemens: pluggable yaylı, adım kablo sınıfına göre** | Kullanıcı onayı |
| **D-69** | **Host giriş 12–48 V** — 12 V leisure + **48 V ESS doğrudan** | Kullanıcı onayı |
| **D-70** | **İlk kasa = tam ürün:** 8U node alanı + 2U host yuvası, 3D baskı | Kullanıcı onayı |
| **D-57** | **Pasif soğutma** — üründe fan yok | Kullanıcı onayı |
| **D-72** | **Node katalogu** — [09 §5](09-node-aileleri.md#5-node-katalogu) | Kullanıcı onayı |
| **D-73** | **AI portu konfigüre** — NTC / 4–20 mA / 0–20 mA / 0–10 V | Kullanıcı onayı |
| **D-74** | **COM-1U** — CAN izolesiz + Ethernet magjack | Kullanıcı onayı |
| **D-24** | **Hot-plug v1 desteklenir** — canlı tak-çıkar birinci sınıf | Kullanıcı onayı |
| **D-18 / D-22 / D-23 / D-34** | **Hot-plug mekanizması** — PCA9555 INT, RST# pull-down, load switch, canlı discovery | D-24 ile kilitlendi |
| **D-16** | **2U mating:** elektrik yalnız sol; sağda bakırsız yalancı dil | Kullanıcı onayı |
| **D-45** | **Ön tutucu = kapalı vida** — hot-plug elektrik; vida tutma | Kullanıcı onayı |
| **D-61** | **1U = 14.4 mm.** Sığmazsa 2U — baskı yok, kanal kesilmez | Kullanıcı onayı |
| **D-29 / D-31** | **+5V: 2.0 A sürekli / 3 A limit.** 1U 250 mA, 2U 500 mA, node havuzu 1.6 A | Kullanıcı onayı |
| **D-10..D-13 / D-30 / D-33** | **Kapalı bus:** RS-485, 2 tel, 500 kbaud, lumped, çerçeve+polling kilit | Kullanıcı onayı |
| **D-03** | **WiFi anten: U.FL + kasa dışı** (pigtail / SMA) — PCB anten yok | Kullanıcı onayı |
| **D-09** | **Giriş: high-side koruma kontrolcüsü + N-FET.** GND bütün. VIN izole değil | Kullanıcı onayı + yönlendirme |
| **D-36** | **Tüm node 2 katman.** 4 katman yok — 2U veya modül bölünür | Kullanıcı onayı |
| **D-62 / D-63** | **Proto 3D+Al kızak · seri Al ekstrüzyon.** Boş slot kör kapak zorunlu | Kullanıcı onayı |
| **D-64** | **AC: IP20 fiş + PCB'de 230 V adası klipsli bariyer.** Tam kutu yok | Kullanıcı onayı |
| **D-53** | **Latching geri okuma = yardımcı kontak** (tüm SKU) | Kullanıcı onayı |
| **D-77** | **Glitch heal:** latching aux; DO/AO host kalıcı imaj. S3 ≠ glitch | Kullanıcı onayı |
| **D-54** | **32/64 A ısı: Al kızak + metal ön panel** | Kullanıcı onayı |
| **D-55** | **AC: sinüste sıfır geçişi; inverter'de rastgele + snubber** | Kullanıcı onayı |
| **D-48** | **Buck: Iq + hafif yük/PFM** — tepe verim değil | Kullanıcı onayı |
| **D-40 / D-41 / D-42 / D-43** | **Enerji:** 20/10/1 Hz · STOP+start-bit · iki buck · VIN+LVD (S3 otomatik değil) | Kullanıcı onayı |
| **D-49** | **Xevr:** alıcı Iq **≤ 0.5 mA** + glitch-free (D-24). Shutdown yok | Kullanıcı onayı |
| **D-78** | **Bilgi modeli: JSON şema + akıllı req/res.** Host API proxy. Tel D-30 ikili. Modbus ızgara native değil | Kullanıcı onayı |
| **D-67** | **BLE v1** butonsuz WiFi uyandırma. Aynı U.FL. S3'te kapalı | Kullanıcı onayı |

---

## Sıradaki iş

Donanım sözleşmesi kilitli. Açık: firmware oturumu (D-25/26/35/50). İlk PCB: **DI-8** (D-28).

---

## Karar tablosu

### Host

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-01 | Host MCU / SoC | ESP32-S3-WROOM-1U-N16R8 | 🟢 | [02](02-host-mimarisi.md#1-mcu-seçimi) |
| D-02 | Ethernet kontrolcüsü | W5500 — **host'ta değil.** Yalnız gelecekteki Ethernet haberleşme node'u kapsamında geçerli · *D-47 ile yeniden kapsamlandırıldı* | 🟢 | [02 §2](02-host-mimarisi.md#2-ethernet-hosttan-çıkarıldı) |
| D-03 | WiFi anten | **U.FL + kasa dışı anten** (pigtail/SMA). PCB anten yok. Modül `-1U` | 🟢 | [02 §3](02-host-mimarisi.md#3-wifi) |
| **D-65** | **WiFi varsayılan kapalı** | Butonla 10 dk açılır. 3.5 → 2.2 Wh/gün, batarya 170 → 273 gün | 🟢 |
| **D-67** | **BLE uyandırma v1** | Light sleep advertising ~1–3 mW. Telefon yaklaşınca WiFi. **S3'te kapalı.** Aynı U.FL (D-03). Buton kalır (D-65) | 🟢 | [02 §3.2](02-host-mimarisi.md#32-uyandırma-mekanizması) |
| **D-66** | **Host = 2U blade, özel slot** | Şasi 250 → 185 mm. Node'larla aynı mekanik, farklı konnektör + keying | 🟢 |
| D-07 | Saha RS-485 izolasyonu | **İzole** + güç kapılı. İzolesiz PLC yok — karavan dahil | 🟢 | [02](02-host-mimarisi.md#4-rs-485-saha-portu) |
| ~~D-27~~ | Modbus register haritası | ⛔ **superseded by D-78** — 0x100 ızgara native sözleşme değil | ⛔ | [02 §6](02-host-mimarisi.md#6-bilgi-modeli-ve-host-api) |
| **D-78** | **Bilgi modeli + host API** | **JSON şema / req-res native.** Host API node modellerine proxy. Tel: D-30. Şema firmware'de | 🟢 | [02 §6](02-host-mimarisi.md#6-bilgi-modeli-ve-host-api) |
| D-47 | Ethernet | **Host'tan çıkarıldı** — haberleşme node'u olarak sunulacak | 🟢 | [10 §8](10-enerji-butcesi.md#8-ethernet-kararı) |

### Enerji bütçesi — birincil kısıt

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-39 | Güç durumları | S0/S1/S2 anahtar ON iken. **S3 yalnız anahtar OFF** (otomatik depo yok) · D-44 | 🟢 | [10 §4](10-enerji-butcesi.md#4-güç-durumları) |
| D-40 | Tarama hızı | **20 / 10 / 1 Hz.** 200 Hz yok | 🟢 | [10 §2.1](10-enerji-butcesi.md#21-tarama-hızı-gerçekte-ne-olmalı) |
| D-41 | Wake-on-bus | Node **STOP**, USART start-bit uyanış. Alıcı açık kalır | 🟢 | [10 §3](10-enerji-butcesi.md#3-wake-on-bus-nodeların-uyuması) |
| D-42 | İki dönüştürücü | Housekeeping Iq ≤ 25 µA + ana 5 V buck EN (S3 kapalı) | 🟢 | [10 §7.1](10-enerji-butcesi.md#71-iki-dönüştürücülü-yapı--d-42) |
| D-43 | Batarya + LVD | **VIN ADC zorunlu.** LVD = uyarı + yük atma. S3'e otomatik inmez (D-44) | 🟢 | [10 §9.1](10-enerji-butcesi.md#91-batarya-izleme--lvd--d-43) |
| D-44 | Uyandırma + güç anahtarı | **Aç-kapa var.** ON+VIN → S0/S1/S2 (S3'e kaçmaz). S3 yalnız OFF. Uyanış: anahtar ON **veya** şarj/şebeke | 🟢 | [10 §9.2](10-enerji-butcesi.md#92-uyandırma-kaynakları) |

### Güç

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-04 | Hedef ortam sıcaklığı | **60 °C** | 🟢 | [03 §6](03-guc-mimarisi.md#6-termal-analiz) |
| **D-69** | **Host giriş aralığı** | **12–48 V DC sürekli** — 12 V leisure batarya ve **yeni ESS'lerin 48 V'u doğrudan**. Ara SKU (8–32 V) yok | 🟢 | [01 §3](01-sistem-genel-bakis.md#3-tasarımı-yöneten-kısıtlar) |
| D-08 | Backplane rail topolojisi | **Tek ray: sadece +5V, koşulsuz** — yüksek gerilim gereken node kendi boost'unu yapar | 🟢 | [03 §2](03-guc-mimarisi.md#2-rail-topolojisi) |
| D-09 | Giriş koruma | **High-side kontrolcü + N-FET** (ideal diyot / OV-UV). Downstream 60 V. GND'de FET yok. VIN izole değil | 🟢 | [03 §1](03-guc-mimarisi.md#1-giriş-koruma-katı) |
| D-29 | Slot güç bütçesi | **1U 250 mA · 2U 500 mA · node havuzu ≤ 1.6 A.** Darbe ayrı (≤800 mA @5 V, D-68) | 🟢 | [03 §4](03-guc-mimarisi.md#4-güç-bütçesi) |
| D-31 | Ana buck | **5 V @ 2.0 A sürekli, limit ≥ 3.0 A** | 🟢 | [03 §3](03-guc-mimarisi.md#3-ana-dönüştürücü) |
| D-48 | Dönüştürücü seçim | **Iq + hafif yük/PFM birincil.** 2 A tepe verim değil | 🟢 | [10 §7.2](10-enerji-butcesi.md#72-dönüştürücü-seçim-kriterleri--d-48) |

### Backplane ve mekanik

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| ~~D-14~~ | Konnektör tipi (26 pin) | ⛔ **superseded by D-32** — kart kenarı/gold finger tercihi korundu, pin sayısı 26 → 12 | ⛔ | [04 §5.3](04-backplane-mekanik.md#53-neden-26-değil-12-tarihsel-karşılaştırma) |
| **D-60** | **Mekanik paradigma** | **Gerçek blade** — şasi + kızak, çıplak PCB. Kutu-içinde-kutu terk edildi | 🟢 | [04 §1](04-backplane-mekanik.md#1-mekanik-mimari-blade-mi-kutu-içinde-kutu-mu) |
| **D-61** | **1U yükseklik** | **14.4 mm tavan.** 1U dene; sığmazsa **2U** (kanal aynı). Egzotik parça dayatılmaz | 🟢 | [04 §2.1](04-backplane-mekanik.md#21-bileşen-yüksekliği--d-61) |
| D-62 | Şasi malzemesi | **Proto: 3D + Al kızak. Seri: Al ekstrüzyon** + sac panel | 🟢 | [04 §3.2](04-backplane-mekanik.md#32-şasi-malzemesi--d-62) |
| D-63 | Boş slot | **Kör kapak zorunlu** — pasif baca kısa devre olmasın | 🟢 | [04 §3.4](04-backplane-mekanik.md#34-boş-slotlar--d-63) |
| D-64 | AC şebeke | **IP20 fiş (D-38) + PCB 230 V adası klipsli bariyer.** Tam kutu yok | 🟢 | [04 §1.1](04-backplane-mekanik.md#11-bladein-bedeli-ve-karşılığı) |
| D-15 | 1U mekanik adım | **17.5 mm, 2U = 35 mm** (D-58 ile birleşti) | 🟢 | [04 §2](04-backplane-mekanik.md#2-slot-ve-node-ölçüleri) |
| D-16 | 2U mating | **Sol elektrik + sağ bakırsız yalancı dil** — N+1 PRESENT# yüksek | 🟢 | [04 §7](04-backplane-mekanik.md#7-2u-node-stratejisi) |
| D-32 | Backplane pinout | **12 pin** (8 fonksiyonel + 4 rezerve), 4 kademeli mate | 🟢 | [04 §5](04-backplane-mekanik.md#5-pinout) |
| D-24 | Hot-plug | **v1 desteklenir** — canlı tak-çıkar birinci sınıf; sonradan rewrite yok | 🟢 | [04 §8](04-backplane-mekanik.md#8-hot-plug-değerlendirmesi) |
| D-45 | **Titreşim / tutma** | **Kapalı vida** (1U: 1 · 2U: 2). Mandal yok. Hot-plug durur — vida 10 sn | 🟢 | [04 §3.3](04-backplane-mekanik.md#33-takma--çıkarma) · [10 §9.3](10-enerji-butcesi.md#93-titreşim) |

### Dahili haberleşme

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-10 | Fiziksel katman | **RS-485** diferansiyel. TTL elendi. Glitch-free xcvr (D-24) | 🟢 | [05 §1](05-dahili-bus.md#1-fiziksel-katman-kararı) |
| D-11 | Dupleks | **Yarım dupleks 2 tel.** Tam dupleks rezervesi yok | 🟢 | [05 §2](05-dahili-bus.md#2-yarım-dupleks-mi-tam-dupleks-mi) |
| D-12 | Baud | **500 kbaud, v1 sabit.** Saha menüsü yok | 🟢 | [05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi) |
| D-13 | Sonlandırma | **Yansıma sonlandırması yok** · fail-safe bias host'ta | 🟢 | [05 §3](05-dahili-bus.md#3-sonlandırma-analizi) |
| D-30 | Çerçeve | SYNC+ADDR+FUNC+LEN+PAYLOAD+CRC16, max 70 byte | 🟢 | [05 §6](05-dahili-bus.md#6-çerçeve-formatı) |
| D-33 | Trafik | Katı host-node polling · arıza latch + poll | 🟢 | [05 §5](05-dahili-bus.md#5-trafik-modeli) |
| D-21 | SYNC | **Pin yok** — 0x0F broadcast çerçeve | 🟢 | [05 §9](05-dahili-bus.md#9-sync-donanım-pini-değil-broadcast-çerçeve) |
| D-49 | Transceiver seçim kriteri | **Alıcı boşta ≤ 0.5 mA + glitch-free (D-24).** Shutdown yok. Parça şemada | 🟢 | [10 §3.1](10-enerji-butcesi.md#31-neden-rs-485-alıcısı-kapatılmıyor) |

### Slot yönetimi

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-17 | Slot adresleme | **Host atar** — ADDR pinleri yok, RST# ile izole enumerasyon | 🟢 | [06 §1](06-slot-yonetimi.md#1-slot-adresleme) |
| D-18 | Presence + reset | Tek PCA9555, INT# — **canlı** tak-çıkar (D-24) | 🟢 | [06 §3](06-slot-yonetimi.md#3-host-tarafı-io-genişletme) |
| D-19 | Bootloader girişi | **BOOT# pini yok** — RST# + ~30 ms bootloader penceresi | 🟢 | [06 §5](06-slot-yonetimi.md#5-bootloadera-giriş) |
| D-20 | Arıza bildirimi | **FAULT# pini yok** — node latch'ler, host poll eder | 🟢 | [06 §4](06-slot-yonetimi.md#4-arıza-bildirimi) |
| D-22 | Reset varsayılanı | Node'da 10k pull-down → varsayılan reset'te | 🟢 | [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) |
| D-23 | Slot başına koruma | Akım sınırlı load switch — S3 + **hot-plug soft-start** | 🟢 | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |
| D-34 | Discovery | Presence → IDENTIFY → bütçe → CONFIG → ENABLE — **canlı** da aynı | 🟢 | [06 §8](06-slot-yonetimi.md#8-discovery-akışı) |

### Firmware

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-25 | Node bootloader yapısı | **Firmware oturumu.** Donanım: BOOT# yok (D-19), RST# + bus var | ⚪ | [07 §2](07-firmware-update.md#2-bootloader-yapısı) |
| D-26 | Host OTA | **Firmware oturumu.** ESP32 çift partisyon aday | ⚪ | [07 §5](07-firmware-update.md#5-host-ota) |
| D-35 | Node FW dağıtımı | **Firmware oturumu.** Aday: host bus üzerinden yazar | ⚪ | [07 §1](07-firmware-update.md#1-dağıtım-modeli) |
| D-50 | Güç durumu firmware'i | **Firmware oturumu.** S0–S3 + D-77 donanımda kilitli | ⚪ | [10 §10](10-enerji-butcesi.md#10-firmware-sorumlulukları) |

### EMC ve üretim

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-06 | EMC hedef seviyesi | **Sertifikasyon yok** — seviye A (ESD + EFT) | 🟢 | [08 §4](08-emc-koruma.md#4-uyumluluk-hedefi) |
| D-05 | Host katman sayısı | **2 katman** — üç gerekçe de çözüldü (D-06, D-47, D-31) | 🟢 | [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı) |
| D-36 | Node katman | **2 katman, istisnasız.** Sığmazsa 2U veya SKU bölünür — 4 katman yok | 🟢 | [08 §5.1](08-emc-koruma.md#51-nodelar-2-katman--d-36) |

### Çıkış node'ları ve mekanik referans

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-51 | DC / AC ayrımı | Ayrı node'lar, **AC yalnız 2U**, SELV ile karışmaz | 🟢 | [11 §4](11-cikis-node-topolojileri.md#4-dc-ac-ayrımı) |
| D-52 | Çıkış node yapısı | **Tek teknoloji / node.** MOSFET DO **8 × 8 A, 1U**. 8 A latching SKU yok. Güç/AC: 1U veya 2U, **4U yok** — kanal düşer · D-75 | 🟢 | [09 §5](09-node-aileleri.md#5-node-katalogu) |
| **D-75** | **Maks. form** | **2U.** 4U yok | 🟢 | [09 §6](09-node-aileleri.md#6-1u--2u-kuralı) |
| D-53 | Latching geri okuma | **Yardımcı kontak**, tüm latching. Gerilim ölçümü yok | 🟢 | [11 §7.3](11-cikis-node-topolojileri.md#73-durum-geri-okuma--d-53) |
| **D-77** | **Glitch heal** | ON iken VIN/5 V kesisinde iyileş. Latching = aux. MOSFET/AO = host persist | 🟢 | [11 §7.3.1](11-cikis-node-topolojileri.md#731-glitch-heal--d-77) |
| **D-68** | **Anlık akım** | Rafta **tek bobin**. Tepe **≤ 800 mA @5 V** (12/24 V boost dahil). Buck limiti 3 A | 🟢 | [03 §5](03-guc-mimarisi.md#5-anlık-akım--röle-darbeleri) |
| D-54 | 32/64 A ısı | **Al kızak + metal ön panel.** PCB bakır yetmez. 8 A'de panel şart değil | 🟢 | [11 §6.3](11-cikis-node-topolojileri.md#63-ısı-yolu--d-54) |
| D-55 | AC sıfır geçişi | **Sinüste ZC.** İnverter/bozuk dalgada rastgele + RC snubber | 🟢 | [11 §4.1](11-cikis-node-topolojileri.md#41-sıfır-geçişi-zero-cross--d-55) |
| **D-56** | **Terminoloji** | **Host / Node** — 14 dokümanda uygulandı | 🟢 | [12 §1.1](12-mekanik-referans-rev01.md#11-terminoloji) |
| **D-57** | **Soğutma** | **Pasif.** Üründe fan yok. Isı yolu: blade PCB → kanal + Al kızak/şasi. Node dissipasyonu bu bütçeye sığmak zorunda | 🟢 | [04 §6](04-backplane-mekanik.md#6-hava-akışı-ve-termal) |
| **D-70** | **İlk kasa** | **Tam zarf:** 8U node + 2U host yuvası. 3D baskı ile basılır. 2–3 slot ara form yok — daha maliyetli | 🟢 | [04 §3](04-backplane-mekanik.md#3-şasi-ve-kızak-sistemi) |
| **D-58** | **Slot adımı 17.5 mm** | Draft benimsendi — cihaz 40 mm daha dar, 2U = 35 mm | 🟢 | [12 §3.1](12-mekanik-referans-rev01.md#31-slot-adımı-175-mm-kabul-edilmeli) |
| D-59 | Backplane 3.3V rail | **Dağıtılmıyor, pin de rezerve edilmiyor** — kullanmamaya karar verilen şeye pin ayırmak tutarsızdı | 🟢 | [12 §3.3](12-mekanik-referans-rev01.md#33-backplane-rail-sayısı-33v-tartışmalı) |

### Node tipleri

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-28 | İlk node | **DI-8** — 8 kanal, 1U, **5–30 V izole** (D-76) | 🟢 | [09 §2](09-node-aileleri.md#2-ilk-node-seçimi) |
| **D-76** | **DI saha** | **~5–30 V, opto izole** — 12 V karavan ve 24 V pano aynı donanım | 🟢 | [09 §2](09-node-aileleri.md#2-ilk-node-seçimi) |
| **D-72** | **Katalog** | [09 §5](09-node-aileleri.md#5-node-katalogu) — 10 SKU | 🟢 | [09 §5](09-node-aileleri.md#5-node-katalogu) |
| **D-73** | **AI-8 port modu** | Kanal başı: NTC / 4–20 mA / 0–20 mA / 0–10 V | 🟢 | [09 §5.2](09-node-aileleri.md#52-analog) |
| **D-74** | **COM-1U** | CAN **izolesiz** + Ethernet (magjack izole). 1U | 🟢 | [09 §5.4](09-node-aileleri.md#54-haberleşme) |
| D-37 | Node MCU | **Tek SKU tüm node'lar: STM32G071 128 KB sınıfı** (STOP, donanım DE). Parça no LCSC'de aday | 🟢 | [09 §3](09-node-aileleri.md#3-node-mcusu) |
| D-38 | Saha klemens | **Pluggable yaylı.** Adım sınıfa göre. **8 A DO = 3.5 mm / 2.5 mm²**; 4 mm² yalnız 16 A+ | 🟢 | [09 §4](09-node-aileleri.md#4-saha-bağlantısı) |
| D-46 | Uygulama bağlamı | **Karavan yönetimi** — batarya beslemeli, hareketli araç | 🟢 | [01 §3](01-sistem-genel-bakis.md#3-tasarımı-yöneten-kısıtlar) |

---

## Karar değişikliği geçmişi

| Tarih | ID | Değişiklik | Gerekçe |
|-------|----|-----------|---------|
| 2026-09-16 | — | İlk taslak oluşturuldu | — |
| 2026-09-16 | D-01, D-02 | 🟡 → 🟢 | Kullanıcı onayı |
| 2026-09-16 | D-04 | 🔴 → 🟢 **60 °C** | Karavan: kapalı mekân, güneş altında 50 °C rahat görülür |
| 2026-09-16 | D-06 | 🔴 → 🟢 **sertifikasyon yok** | Kullanıcı: önemsiz |
| 2026-09-16 | D-46 | Yeni — karavan bağlamı | Enerji bütçesini birincil kısıt yapıyor |
| 2026-09-16 | D-39..D-45, D-47..D-50 | Yeni — enerji bütçesi kararları | [10](10-enerji-butcesi.md) |
| 2026-09-16 | **D-40** | **200 Hz → 20/10/1 Hz uyarlanabilir** | 200 Hz endüstriyel varsayımdı; node'ların uyumasını engelliyordu |
| 2026-09-16 | **D-31** | **3A → 2A** | Wake-on-bus ile gerçekçi slot tüketimi düştü; 200 mA/slot varsayımı fazla cömertti |
| 2026-09-16 | **D-05** | Gerekçe değişti | D-06 (sertifikasyon yok) EMC gerekçesini zayıflattı; D-31 (2A) termal gerekçeyi zayıflattı. Artık zorunlu değil. |
| 2026-09-16 | D-29 | Toplam limit eklendi | Descriptor güç beyanı ile ≤ 1.6 A zorlanıyor |
| 2026-09-16 | D-51..D-55 | Yeni — çıkış node'u topolojileri | [11](11-cikis-node-topolojileri.md) |
| 2026-09-16 | D-56..D-59 | Yeni — mekanik draft Rev 0.1 ile uzlaştırma | [12](12-mekanik-referans-rev01.md) |
| 2026-09-16 | **D-58** | **Slot adımı 22.5 → 17.5 mm** | Çalışma draftı; cihaz 40 mm daralıyor, 17.5 mm de DIN standardı |
| 2026-09-16 | **[11 §6.1] düzeltme** | **Termal hesap hatalıydı** | Paketlenmiş node'da yan yüzeyler havaya bakmıyor — 5× hata. Fan zorunlu. |
| 2026-09-16 | **D-56** | 🟡 → 🟢 **Host / Node** | Draft'taki ürün dili benimsendi, 14 dokümanda uygulandı |
| 2026-09-16 | **D-47** | 🟡 → 🟢 **Ethernet host'tan çıkarıldı** | 495 mW ile en büyük sürekli yüktü. RS-485 2 tel aynı işi ~$0.20 ve çok daha az enerjiyle yapıyor. Modbus TCP WiFi üzerinden sürüyor; kablolu Ethernet isteyen haberleşme node'u takar |
| 2026-09-16 | **D-52** | 🟡 → 🟢 **4 kanal, tek teknoloji/node** | Daha basit, daha modüler. 3.5 mm push-in ile 5 kutup tam 17.5 mm ediyor |
| 2026-09-16 | **D-58** | 🟡 → 🟢 **17.5 mm slot adımı** | Cihaz 40 mm daralıyor; 17.5 mm de DIN standardı |
| 2026-09-16 | **D-31** | 2A → **1.5A** | Ethernet çıkınca host tepe yükü 380 → 290 mA düştü |
| 2026-09-16 | **D-05** | 🟡 → 🟢 **2 katman** | D-06, D-47 ve D-31 üç gerekçeyi de ortadan kaldırdı. Brief'in 2 katman tercihine dönüldü |
| 2026-09-16 | D-29 | 200 → 150 mA/slot, toplam 1.2 A | D-31 ile uyum |
| 2026-09-16 | **D-60** | Yeni — **gerçek blade mimarisi** | Kutu-içinde-kutu her node'un etrafına plastik yalıtım koyuyordu. Blade'de PCB doğrudan hava kanalında: termal çözülüyor, node başına $2–5 muhafaza maliyeti kalkıyor, kızak PCB'yi titreşime karşı 110 mm boyunca destekliyor |
| 2026-09-16 | D-15 | 22.5 → 17.5 mm, D-58 ile birleşti | Tek karar olarak izlenecek |
| 2026-09-16 | D-57 | Fan bütçesi 0.5–1.5 W → **~0.2 W** | Gerçek debi ihtiyacı 1.6 CFM çıktı; blade mimarisi debiyi düşürdü |
| 2026-09-16 | D-61..D-64 | Yeni — blade mekaniğinin getirdikleri | Bileşen yüksekliği, şasi malzemesi, kör kapak, AC bariyeri |
| 2026-09-16 | 04 | **Baştan yazıldı** | Blade mimarisi + 17.5 mm + hava akışı bölümü eklendi |
| 2026-09-16 | **D-65** | Yeni — **WiFi varsayılan kapalı** | WiFi'ın maliyeti varlığı değil sürekli bağlı kalması. Tamamen atmakla talep üzerine açmak arasında %14 fark var; atmak ise ESP32'den vazgeçmeyi ve fiziksel HMI eklemeyi gerektirir ki o daha pahalı |
| 2026-09-16 | **D-66** | Yeni — **host 2U blade** | Ayrı bölme gereksizdi: blade PCB yüz alanı (75×110) host için fazlasıyla yeterli. 2U, alan için değil bileşen yüksekliği için. Şasi 65 mm daralıyor |
| 2026-09-16 | D-67 | Yeni — BLE uyandırma | Butonsuz UX, ~1–3 mW |
| 2026-09-16 | Enerji bütçesi | 3.5 → **2.2 Wh/gün** | D-65; batarya ömrü 170 → 273 gün |
| 2026-09-16 | **D-32** | **26 → 12 pin** | Uçtan uca sorgulama. GND 4→2 (akım için 1 bile yeter, 2'si titreşim redundansı), VBUS_RAW çıktı, ADDR çıktı, BOOT#/FAULT#/SYNC çıktı, rezerve 6→4 |
| 2026-09-16 | **D-08** | İkili ray → **tek +5V rayı** | 12–48 V'un tek gerçek müşterisi analog çıkış compliance'ıydı; o node'a $0.30 boost, 8 slota 2 pin + yüksek gerilimden ucuz |
| 2026-09-16 | **D-17** | Coğrafi → **host atamalı** | Per-slot RST# zaten çakışmasız enumerasyon mekanizması. Node'un konumunu bilmesinin işlevsel karşılığı yoktu |
| 2026-09-16 | **D-19** | BOOT# pini → **bootloader penceresi** | Kilitlenmiş app reset sonrası zaten çalışmıyor; RST# yeterli |
| 2026-09-16 | **D-20** | FAULT# pini → **poll** | 100 ms gecikme önemsiz; gerçek zamanlı koruma node'un işi. Wired-OR'un maskeleme arıza modu da gitti |
| 2026-09-16 | **D-21** | SYNC pini → **broadcast çerçeve** | Bus zaten broadcast; µs ile ns farkı bu uygulamada ölçülemez |
| 2026-09-16 | D-11, D-59 | Rezerve pinler 6 → 4 | Tam dupleks senaryosu gerçekçi değil; 3.3V'a zaten hayır denmişti |
| 2026-09-16 | **D-08** | Koşullu → **koşulsuz** | 5 V bobin bulunabilirliği karara gömülü bir tedarik riskiydi. Yüksek gerilim gereken node kendi boost'unu yapıyor (~$0.30) — bağımlılık tamamen kalktı |
| 2026-09-16 | **D-68** | Yeni — anlık akım yönetimi | Röle bobinleri rafta 2.6 A tepe yaratabilir. Bulk kapasitörle karşılamak 66 mF gerektiriyor, yani imkânsız. Sıralama optimizasyon değil yapısal gereklilik |
| 2026-09-16 | D-61 | Kısıt daraldı | Latching röle aramasında bobin gerilimi artık filtre değil — sadece yükseklik ve şok değeri |
| **2026-09-17** | **D-14** | 🟡 → ⛔ **superseded by D-32** | 26 pin aktif öneri gibi duruyordu; kart kenarı/gold finger tercihi korundu, pin sayısı 12'ye indi |
| **2026-09-17** | **D-02** | Kapsam daraltıldı | W5500 host Ethernet kontrolcüsü olarak görünüyordu; D-47 ile çelişiyordu. Artık yalnız gelecekteki Ethernet haberleşme node'u kapsamında |
| **2026-09-17** | **D-56** | Statü birleştirildi | Üstte 🟢, tabloda 🟡 görünüyordu — 🟢'ye sabitlendi |
| **2026-09-17** | **D-25** | İfade düzeltildi | "BOOT# donanım kaçışı" diyordu; BOOT# D-19 ile kaldırılmıştı. RST# + bootloader penceresi olarak yazıldı |
| **2026-09-17** | **D-52** | Statü birleştirildi | Kabul listesinde 🟢, tabloda 🟡 görünüyordu — 🟢'ye sabitlendi |
| **2026-09-17** | — | Consistency review | 20 çelişki düzeltildi; yeni mimari karar üretilmedi |
| **2026-09-17** | **D-28** | 🔴 → 🟢 **DI 8ch 1U** | Kullanıcı: çekirdek doğrulama node'u bu. Katalog sonraki iş — her node tam spec, "aile" dili yok |
| **2026-09-17** | **D-69** | Yeni — **host 12–48 V** | Yeni ESS'ler 48 V; leisure 12 V. Tek host SKU, ara gerilim kesiti yok |
| **2026-09-17** | **D-70** | Yeni — **ilk kasa tam 8U+2U** | Ara 2–3 slot form daha maliyetli. Hedef bütünsel; 3D baskı ile tam zarf |
| **2026-09-17** | **D-57** | 🟡 fan → 🟢 **pasif soğutma** | Fan cihaz için her zaman sorun. Odak: iletim (Al kızak) + baca; dissipasyon node spec'ine düşer |
| **2026-09-17** | **D-52** | 4ch → **MOSFET DO 8×8 A 1U**; 8 A latching düştü | 1 A vs 8 A maliyet önemsiz; tek standart DO. PWM aynı donanım |
| **2026-09-17** | **D-72..D-75, D-51** | Katalog + AI config + COM CAN/ETH + max 2U; D-51 🟢 | 4U yok, kanal düşer. AI/AO ayrı 1U |
| **2026-09-17** | **D-76** | Yeni — **DI 5–30 V izole** | 12 V karavan + 24 V pano tek kart |
| **2026-09-17** | **D-37** | ⚪ → 🟢 **G071 128 KB, tüm node'lar** | Tek SKU, tek toolchain. COM sıkışırsa G0B1 aynı paket |
| **2026-09-17** | **D-38** | ⚪ → 🟢 **pluggable yaylı, adım sınıfa göre** | DC 4–6 mm² bol; 3.5 mm her modüle değil. 8 A'de 4 mm² açık |
| **2026-09-17** | **D-38** | 8 A DO **2.5 mm² / 3.5 mm** | 8 A için 2.5 mm² safe; 4 mm² 16 A+ |
| **2026-09-17** | **D-07** | 🟡 → 🟢 **saha RS-485 izole** | İzolesiz PLC yok; karavan hobi olsa da yakılan donanım olmasın |
| **2026-09-17** | **D-74** | CAN **izolesiz**; ETH magjack izole | 1U yer; BMS/Victron ortak şasi |
| **2026-09-17** | **D-24** | 🟡 → 🟢 **v1 hot-plug** | Sonra 1U/enerji/yazılım sürprizi olmasın. D-18/22/23/34 aynı paket 🟢 |
| **2026-09-17** | **D-16** | 🟡 → 🟢 **sol elektrik + bakırsız sağ dil** | Çift elektrik hot-plug'ta yarım mate. Dil stabilite; bakır olsa N+1 sahte node |
| **2026-09-17** | **D-45** | 🟡 → 🟢 **ön kapalı vida** | Mandal yok. Hot-plug baltalanmaz: PRESENT#/bus aynı; vida tutma |
| **2026-09-17** | **D-61** | 🟡 → 🟢 **1U 14.4 mm; sığmazsa 2U** | Baskı yok. Kanal kesilmez. 4U hâlâ yok (D-75) |
| **2026-09-17** | **D-29, D-31** | 🟡 → 🟢 **2.0 A / 3 A** | 1.5 A büyük bobin + 12/24 V boost'a dar. 3 A 2 katmanı yakar. 1U 250 / 2U 500, havuz 1.6 A |
| **2026-09-17** | **D-10..13, D-30, D-33** | 🟡 → 🟢 **kapalı bus** | Üçüncü taraf kart yok. 500 k sabit. Çerçeve+polling predefined |
| **2026-09-17** | **D-03** | 🟡 → 🟢 **U.FL + kasa dışı anten** | Standart. PCB anten metal kasada ölür. SMA/pigtail kasa üzerinde |
| **2026-09-17** | **D-09** | 🟡 → 🟢 **kontrolcü + high-side N-FET** | A/B aynı high-side; B karakterize. VIN izole değil — izolasyon saha (D-07) |
| **2026-09-17** | **D-36** | 🟡 → 🟢 **node 2 katman** | Max 2U standart. COM sığmazsa böl veya 2U; 4 katman yok |
| **2026-09-17** | **D-62, D-63** | 🟡 → 🟢 **Al seri şasi + kör kapak** | Proto 3D+kızak (D-70). Baca için kapak zorunlu |
| **2026-09-17** | **D-64** | 🟡 → 🟢 **PCB 230 V bariyeri** | Kablo D-38 IP20. Node içi ada kapağı; tam kutu yok |
| **2026-09-17** | **D-53** | 🟡 → 🟢 **aux kontak** | Gerilim ölçümü yok. Kör darbe yok |
| **2026-09-17** | **D-77** | Yeni — **glitch heal** | Latching aux gerçeği. DO/AO host persist. S3 ≠ glitch |
| **2026-09-17** | **D-54** | 🟡 → 🟢 **kızak + metal ön panel** | 32/64 A. 8 A'de panel şart değil |
| **2026-09-17** | **D-55** | ⚪ → 🟢 **sinüste ZC** | İnverter'de yok — rastgele + snubber. ZC = 0 V'ta kes |
| **2026-09-17** | **D-48** | 🟡 → 🟢 **Iq + PFM** | Tepe verim boşta yalan. %90 zaman 50–200 mA |
| **2026-09-17** | **D-40..43** | 🟡 → 🟢 **enerji kümesi** | 20/10/1 Hz, STOP, iki buck, LVD. S3 yalnız OFF |
| **2026-09-17** | **D-49** | 🟡 → 🟢 **xcvr Iq** | ≤ 0.5 mA alıcı + glitch-free. Ayrı wake hattı yok |
| **2026-09-17** | **D-78** | Yeni — **JSON + host API** | Enterprise model. D-27 ızgara native değil; SCADA varsa host adapter |
| **2026-09-17** | **D-27** | 🟡 → ⛔ **superseded by D-78** | Slot 0x100 / 0x1000 önerisi kilitlenmedi |
| **2026-09-17** | **D-25/26/35/50** | 🟡 → ⚪ **firmware oturumu** | Şema/codec/BL/OTA birlikte. BOOT# yok (D-19) |
| **2026-09-17** | **D-67** | ⚪ → 🟢 **BLE v1** | Butonsuz WiFi. S3'te advertising yok. Anten D-03 |
