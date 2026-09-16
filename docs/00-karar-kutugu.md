# 00 — Karar Kütüğü

Tüm mimari kararların tek kaynağı. Bir karar burada 🟢 olmadan ilgili donanım
tasarlanmaz. Karar değişirse önce burası güncellenir.

**Son güncelleme:** 2026-09-16 · Karavan bağlamı ve enerji bütçesi eklendi

---

## Özet durum

| Durum | Adet |
|-------|------|
| 🟢 Kabul edildi | 15 |
| 🟡 Öneri hazır, onay bekliyor | 43 |
| 🔴 Dışarıdan bilgi gerekiyor | 1 |
| ⚪ Henüz ele alınmadı | 4 |

---

## Kabul edilen kararlar

| ID | Karar | Kaynak |
|----|-------|--------|
| **D-01** | Host MCU: **ESP32-S3-WROOM-1U-N16R8** | Kullanıcı onayı |
| **D-02** | Ethernet: **W5500** (SPI, donanım TCP/IP) | Kullanıcı onayı |
| **D-04** | Hedef ortam sıcaklığı: **60 °C** | Kullanıcı — kapalı mekân, güneş altında 50 °C rahat görülür |
| **D-06** | EMC: **sertifikasyon hedefi yok**, seviye A (ESD + EFT) | Kullanıcı |
| **D-46** | Uygulama bağlamı: **karavan yönetimi**, batarya beslemeli | Kullanıcı |
| **D-47** | **Ethernet host kartından çıkarıldı** — RS-485 + WiFi yeterli | Kullanıcı onayı |
| **D-52** | **Çıkış node'ları: 4 kanal, her node tek teknoloji** | Kullanıcı onayı |
| **D-56** | **Terminoloji: Host / Node** — tüm dokümanlarda uygulandı | Kullanıcı onayı |
| **D-05** | **Host 2 katman** — üç gerekçe de ortadan kalktı | Türetilmiş |
| **D-58** | **Slot adımı 17.5 mm** (2U = 35 mm) | Çalışma draftı Rev 0.1 |
| **D-60** | **Gerçek blade mimarisi** — şasi + kızak, kutu-içinde-kutu terk edildi | Kullanıcı |
| **D-65** | **WiFi varsayılan kapalı, talep üzerine açılır** | Kullanıcı |
| **D-66** | **Host = 2U blade, kendi özel slotunda** | Kullanıcı |

---

## Bilgi bekleyen kararlar

| ID | Soru | Neyi etkiliyor |
|----|------|----------------|
| **D-28** | İlk örnek node ve node aileleri | İlk şemanın kapsamı. *Kullanıcı ayrıca detaylandıracak.* |

---

## Karar tablosu

### Host

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-01 | Host MCU / SoC | ESP32-S3-WROOM-1U-N16R8 | 🟢 | [02](02-host-mimarisi.md#1-mcu-seçimi) |
| D-02 | Ethernet kontrolcüsü | W5500 — **host'ta değil, haberleşme node'unda** (D-47) | 🟢 | [02](02-host-mimarisi.md#2-ethernet-hosttan-çıkarıldı) |
| D-03 | WiFi anten | U.FL + harici anten (ESP32 `-1U` modül varyantı) | 🟡 |
| **D-65** | **WiFi varsayılan kapalı** | Butonla 10 dk açılır. 3.5 → 2.2 Wh/gün, batarya 170 → 273 gün | 🟢 |
| **D-66** | **Host = 2U blade, özel slot** | Şasi 250 → 185 mm. Node'larla aynı mekanik, farklı konnektör + keying | 🟢 |
| D-67 | BLE ile butonsuz uyandırma | Değerlendirilecek — ~1–3 mW, UX kazancı büyük | ⚪ | [02](02-host-mimarisi.md#3-wifi) |
| D-07 | Saha RS-485 izolasyonu | İzole — ama güç kapılı ([10 §7.3](10-enerji-butcesi.md#73-güç-kapısı-gereksinimleri)) | 🟡 | [02](02-host-mimarisi.md#4-rs-485-saha-portu) |
| D-27 | Modbus register haritası | Slot başına 0x100'lük blok, 0x1000 tabanlı | 🟡 | [02](02-host-mimarisi.md#6-modbus-register-haritası) |
| D-47 | Ethernet | **Host'tan çıkarıldı** — haberleşme node'u olarak sunulacak | 🟢 | [10 §8](10-enerji-butcesi.md#8-ethernet-kararı) |

### Enerji bütçesi — birincil kısıt

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-39 | Güç durumları | S0 Aktif / S1 Boşta / S2 Bekleme / S3 Depo | 🟡 | [10 §4](10-enerji-butcesi.md#4-güç-durumları) |
| D-40 | Uyarlanabilir tarama hızı | 20 / 10 / 1 Hz — 200 Hz terk edildi | 🟡 | [10 §2.1](10-enerji-butcesi.md#21-tarama-hızı-gerçekte-ne-olmalı) |
| D-41 | Wake-on-bus | Node STOP modunda uyur, USART start-bit ile uyanır | 🟡 | [10 §3](10-enerji-butcesi.md#3-wake-on-bus-nodeların-uyuması) |
| D-42 | İki dönüştürücülü yapı | Housekeeping (Iq ≤ 25 µA) + ana buck (EN pinli) | 🟡 | [10 §7.1](10-enerji-butcesi.md#71-iki-dönüştürücülü-yapı) |
| D-43 | Batarya izleme + LVD | VBUS_RAW gerilim ölçümü — **batarya sisteminde zorunlu** | 🟡 | [10 §9.1](10-enerji-butcesi.md#91-batarya-izleme) |
| D-44 | Uyandırma kaynakları | En az 2 RTC GPIO uyandırma girişi | 🟡 | [10 §9.2](10-enerji-butcesi.md#92-uyandırma-kaynakları) |

### Güç

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-04 | Hedef ortam sıcaklığı | **60 °C** | 🟢 | [03 §5](03-guc-mimarisi.md#5-termal-analiz) |
| D-08 | Backplane rail topolojisi | İkili rail: VBUS_RAW (12–48V) + +5V_SYS | 🟡 | [03 §2](03-guc-mimarisi.md#2-rail-topolojisi) |
| D-09 | Giriş koruma topolojisi | Seri FET + gate zener clamp (~55V) → downstream 60V sınıfı | 🟡 | [03 §1](03-guc-mimarisi.md#1-giriş-koruma-katı) |
| D-29 | Slot güç bütçesi | 1U: 150 mA tavan · toplam ≤ 1.2 A (descriptor ile zorlanır) | 🟡 | [03 §4](03-guc-mimarisi.md#4-güç-bütçesi) |
| D-31 | Ana buck tasarım noktası | **5V @ 1.5A** — 3A → 2A → 1.5A | 🟡 | [03 §3](03-guc-mimarisi.md#3-ana-dönüştürücü) |
| D-48 | Dönüştürücü seçim kriteri | **Hafif yük verimi + düşük Iq**, tepe verim değil | 🟡 | [10 §7.2](10-enerji-butcesi.md#72-dönüştürücü-seçim-kriterleri-değişti) |

### Backplane ve mekanik

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-14 | Konnektör tipi | PCB kart kenarı (gold finger), 2.54mm, çift sıra, 26 pin | 🟡 | [04 §4](04-backplane-mekanik.md#4-konnektör-seçimi) |
| **D-60** | **Mekanik paradigma** | **Gerçek blade** — şasi + kızak, çıplak PCB. Kutu-içinde-kutu terk edildi | 🟢 | [04 §1](04-backplane-mekanik.md#1-mekanik-mimari-blade-mi-kutu-içinde-kutu-mu) |
| **D-61** | **1U bileşen yüksekliği** | **14.4 mm bütçe** — latching röleler ≤12 mm olmalı, doğrulanacak | 🟡 | [04 §2.1](04-backplane-mekanik.md#21-bileşen-yüksekliği-bütçesi-kritik-kısıt) |
| D-62 | Şasi malzemesi | Prototip: 3D baskı + Al kızak · Seri: **Al ekstrüzyon** (rijitlik + EMI + ısı yolu) | 🟡 | [04 §3.2](04-backplane-mekanik.md#32-şasi-malzemesi) |
| D-63 | Boş slot kör kapağı | **Zorunlu** — hava akışı kısa devre olmasın | 🟡 | [04 §3.4](04-backplane-mekanik.md#34-boş-slotlar) |
| D-64 | AC node şebeke bariyeri | Klipsli plastik kapak (tam kutu değil) | 🟡 | [04 §1.1](04-backplane-mekanik.md#11-bladein-bedeli-ve-karşılığı) |
| D-15 | 1U mekanik adım | **17.5 mm, 2U = 35 mm** (D-58 ile birleşti) | 🟢 | [04 §2](04-backplane-mekanik.md#2-slot-ve-node-ölçüleri) |
| D-16 | 2U mating stratejisi | Sadece sol slot konnektörüne oturur | 🟡 | [04 §7](04-backplane-mekanik.md#7-2u-node-stratejisi) |
| D-32 | Backplane pinout | 26 pin, 4 kademeli mate sırası | 🟡 | [04 §5](04-backplane-mekanik.md#5-pinout) |
| D-24 | Hot-plug | Donanım yetenekli tasarla, v1'de garanti verme | 🟡 | [04 §8](04-backplane-mekanik.md#8-hot-plug-değerlendirmesi) |
| D-45 | **Titreşim dayanımı** | Node tutucu mandal/vida zorunlu — konnektör tek başına tutmaz | 🟡 | [10 §9.3](10-enerji-butcesi.md#93-titreşim) |

### Dahili haberleşme

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-10 | Fiziksel katman | RS-485 diferansiyel — TTL UART elendi | 🟡 | [05 §1](05-dahili-bus.md#1-fiziksel-katman-kararı) |
| D-11 | Dupleks | Yarım dupleks 2 tel, tam dupleks için 2 pin rezerve | 🟡 | [05 §2](05-dahili-bus.md#2-yarım-dupleks-mi-tam-dupleks-mi) |
| D-12 | Baud hızı | 500 kbaud (konfigüre edilebilir) | 🟡 | [05 §4](05-dahili-bus.md#4-hız-ve-tarama-süresi) |
| D-13 | Sonlandırma | Yansıma sonlandırması yok · fail-safe bias var | 🟡 | [05 §3](05-dahili-bus.md#3-sonlandırma-analizi) |
| D-30 | Çerçeve formatı | SYNC+ADDR+FUNC+LEN+PAYLOAD+CRC16, max 70 byte | 🟡 | [05 §6](05-dahili-bus.md#6-çerçeve-formatı) |
| D-33 | Trafik modeli | Katı host-node polling + donanım FAULT# event hattı | 🟡 | [05 §5](05-dahili-bus.md#5-trafik-modeli) |
| D-21 | SYNC hattı | Var — eşzamanlı I/O latch strobe, 1 pin | 🟡 | [05 §9](05-dahili-bus.md#9-sync-stroboskobu) |
| D-49 | Transceiver seçim kriteri | **Alıcı boşta akımı birincil kriter** (0.5 mA hedef) | 🟡 | [10 §3.1](10-enerji-butcesi.md#31-neden-rs-485-alıcısı-kapatılmıyor) |

### Slot yönetimi

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-17 | Slot adresleme | 4-bit coğrafi (backplane'de sabitlenmiş) | 🟡 | [06 §1](06-slot-yonetimi.md#1-slot-adresleme) |
| D-18 | Presence + reset yönetimi | Tek PCA9555, INT# ile hot-plug algılama | 🟡 | [06 §3](06-slot-yonetimi.md#3-host-tarafı-io-genişletme) |
| D-19 | Bootloader girişi | Ortak BOOT# + hedef slotun RST# bırakılması | 🟡 | [06 §5](06-slot-yonetimi.md#5-boot-stratejisi) |
| D-20 | Fault bildirimi | Ortak open-drain wired-OR FAULT# | 🟡 | [06 §4](06-slot-yonetimi.md#4-fault-hattı) |
| D-22 | Reset varsayılanı | Node'da 10k pull-down → varsayılan reset'te | 🟡 | [06 §6](06-slot-yonetimi.md#6-reset-varsayılan-durumu) |
| D-23 | Slot başına koruma | Akım sınırlı load switch — **S3'ün de mekanizması** | 🟡 | [06 §7](06-slot-yonetimi.md#7-slot-başına-akım-koruması) |
| D-34 | Discovery | Presence → IDENTIFY → bütçe → CONFIG → ENABLE | 🟡 | [06 §8](06-slot-yonetimi.md#8-discovery-akışı) |

### Firmware

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-25 | Node bootloader yapısı | Tek app + CRC + BOOT# donanım kaçışı | 🟡 | [07 §2](07-firmware-update.md#2-bootloader-yapısı) |
| D-26 | Host OTA | ESP32 çift partisyon + rollback | 🟡 | [07 §5](07-firmware-update.md#5-host-ota) |
| D-35 | Node FW dağıtımı | Host, dahili bus üzerinden yazar | 🟡 | [07 §1](07-firmware-update.md#1-dağıtım-modeli) |
| D-50 | Güç durumu firmware'i | S0–S3 durum makinesi, güvenli geçiş, raporlama | 🟡 | [10 §10](10-enerji-butcesi.md#10-firmware-sorumlulukları) |

### EMC ve üretim

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-06 | EMC hedef seviyesi | **Sertifikasyon yok** — seviye A (ESD + EFT) | 🟢 | [08 §4](08-emc-koruma.md#4-uyumluluk-hedefi) |
| D-05 | Host katman sayısı | **2 katman** — üç gerekçe de çözüldü (D-06, D-47, D-31) | 🟢 | [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı) |
| D-36 | Node katman sayısı | 2 katman | 🟡 | [08 §5](08-emc-koruma.md#5-katman-sayısı-kararı) |

### Çıkış node'ları ve mekanik referans

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-51 | DC / AC ayrımı | Ayrı node aileleri, AC minimum 2U (creepage) | 🟡 | [11 §4](11-cikis-node-topolojileri.md#4-dc-ac-ayrımı) |
| D-52 | 8A sınıfı: latching ve MOSFET ayrı node mü? | Ayrı öneriliyor — PWM gerekenler MOSFET, uzun süre açık kalanlar latching | 🟡 | [11 §5.1](11-cikis-node-topolojileri.md#51-dc-çıkış) |
| D-53 | Latching kontak durumu geri okuma | **Zorunlu** — yöntem açık (yardımcı kontak vs gerilim ölçümü) | 🟡 | [11 §7.3](11-cikis-node-topolojileri.md#73-durum-geri-okuma) |
| D-54 | 32A/64A ısı yolu | Alüminyum ray/ön panel üzerinden — draft'taki hibrit yapı uygun | 🟡 | [11 §6.3](11-cikis-node-topolojileri.md#63-ek-termal-önlemler) |
| D-55 | AC'de zero-cross anahtarlama | Açık | ⚪ | [11 §9](11-cikis-node-topolojileri.md#9-açık-sorular) |
| **D-56** | **Terminoloji: Host/Node mu Host/Node mü?** | **Host/Node öneriliyor** (draft'taki ürün dili) | 🟡 | [12 §1.1](12-mekanik-referans-rev01.md#11-terminoloji) |
| **D-57** | **Fan + termostatik kontrol** | **Zorunlu** — doğal konveksiyon pakette yetmiyor; ama sürekli çalışamaz | 🟡 | [12 §3.5](12-mekanik-referans-rev01.md#35-soğutma-fan-ve-benim-termal-hatam) |
| **D-58** | **Slot adımı 17.5 mm** | Draft benimsendi — cihaz 40 mm daha dar, 2U = 35 mm | 🟢 | [12 §3.1](12-mekanik-referans-rev01.md#31-slot-adımı-175-mm-kabul-edilmeli) |
| D-59 | Backplane 3.3V rail | Dağıtılmasın, ama **pin rezerve edilsin** | 🟡 | [12 §3.3](12-mekanik-referans-rev01.md#33-backplane-rail-sayısı-33v-tartışmalı) |

### Node aileleri

| ID | Konu | Karar / Öneri | Durum | Ref |
|----|------|---------------|-------|-----|
| D-28 | İlk örnek node | — *Kullanıcı detaylandıracak* | 🔴 | [09 §2](09-node-aileleri.md#2-ilk-node-seçimi) |
| D-37 | Node MCU ailesi | ⚪ — ön eğilim STM32G0 (STOP modu + donanım DE) | ⚪ | [09 §3](09-node-aileleri.md#3-node-mcusu) |
| D-38 | Saha klemens tipi | ⚪ — **titreşim nedeniyle push-in yaylı öneriliyor** | ⚪ | [09 §4](09-node-aileleri.md#4-saha-bağlantısı) |
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
