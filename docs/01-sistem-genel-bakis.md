# 01 — Sistem Genel Bakış

## 1. Ürün tanımı

**Uygulama bağlamı: karavan yönetimi.** NeoPLC batarya beslemeli, hareketli bir
araçta, kapalı ve güneş altında ısınan bir hacimde çalışacak. Bu bağlam
mimarinin tamamını şekillendiriyor — özellikle [enerji bütçesini](10-enerji-butcesi.md)
birincil kısıt haline getiriyor.

NeoPLC tek bir kart değil, bir **ürün platformudur**. Host birim ve ona takılan
fonksiyon node'larından oluşur. Platformun değeri tek tek kartlarda değil,
node'lar arası **değişmez sözleşmede** (backplane pinout + protokol + mekanik)
yatar.

Bu nedenle bu dokümantasyonun asıl konusu kartlar değil, **sözleşmedir.**

![Sistem ön görünüm](img/01-sistem-onden.svg)

```
┌──────────────────────────────────────────────────────────────┐
│  HOST BİRİM                                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ESP32-S3 · RS-485 · Wi-Fi · Güç katı · Slot yönetimi   │  │
│  └────────────────────────────────────────────────────────┘  │
│  ═════════ BACKPLANE — 8U node kapasitesi ═════════════════  │
│   ┌───┐ ┌───┐ ┌───────┐ ┌───┐ ┌───┐ ┌───────┐               │
│   │1U │ │1U │ │  2U   │ │1U │ │1U │ │  2U   │               │
│   │DI │ │DO │ │  AI   │ │RLY│ │DO │ │ ÖZEL  │               │
│   └───┘ └───┘ └───────┘ └───┘ └───┘ └───────┘               │
│   slot1 slot2  slot3-4  slot5 slot6  slot7-8                 │
└──────────────────────────────────────────────────────────────┘
      ↑ saha bağlantıları node'ların ön yüzünde (klemens)
```

## 2. Bileşenler

### Host birim

Host, **kendine ayrılmış sabit 2U host slotunda** duran bir blade'dir ve
**8U kullanıcı node kapasitesinden tüketmez.** Ürün fiziksel olarak
**2U host + 8U node** şeklindedir. **İlk kasa bu tam zarftır** (D-70) —
ara slot sayılı form yok; prototip 3D baskı ile aynı zarfta basılır.

Sorumlulukları:

- 12–48V giriş koruması ve sistem güç üretimi
- 8U node kapasitesinin beslenmesi, güç bütçesi zorlaması, arıza izolasyonu
- Node discovery, konfigürasyon, sağlık takibi
- Dahili bus yöneticiliği (deterministik tarama)
- Dış haberleşme: **RS-485 / Modbus RTU** (saha) ·
  **Wi-Fi** (varsayılan kapalı; talep üzerine web UI, OTA, **Host API** · D-78)
- Node firmware dağıtımı
- Web tabanlı konfigürasyon arayüzü

### Takılabilir node'lar

1U (1 slot) veya 2U (2 slot) genişliğinde. Her node kendi I/O fonksiyonunu
**lokal olarak** yönetir: filtreleme, debounce, ölçekleme, kanal seviyesinde hata
takibi node'un kendi MCU'sunda yapılır.

Host yalnızca anlamlı durumu okur — ham gerçek zamanlı I/O detayını değil. Bu,
host'un yükünü sabitler: 8 node de 64 kanal de olsa, host'un işi slot başına
tek bir proses imajı alışverişidir.

## 3. Tasarımı yöneten kısıtlar

Tüm mimari kararlar bu üç kısıttan türüyor. Bir karar tartışılırken önce hangi
kısıta hizmet ettiği sorulmalı.

| # | Kısıt | Türettiği kararlar |
|---|-------|--------------------|
| **K1** | 8U node kapasitesi × düşük maliyetli node | Node elektroniği ucuz ve az pinli olmalı. Karmaşıklık host'a yığılır — orada bir kez ödenir, node'da sekiz kez. |
| **K2** | **12–48V host girişi** · D-69 | **12 V leisure ve 48 V ESS aynı host SKU.** 48 V nominal → transient sonrası ~90 V. Ön kat gerilim sınıfını bu belirliyor. Ara 8–32 V kesiti yok. |
| **K3** | 2 katman tercihi | Kontrollü empedans pratikte elenir. Bu kısıt MCU seçimini ve yüksek hızlı arayüzlerin tasarıma girip girmeyeceğini belirledi. *(Seçim döneminde Ethernet kontrolcüsü tercihini de bu kısıt şekillendirmişti; Ethernet sonradan host'tan çıkarıldı — D-47.)* |
| **K4** | **Batarya beslemesi — enerji bütçesi** | **Boşta tüketim ürünün yaşayabilirliğini belirliyor.** Sürekli çalışan her bileşen sorgulanır; uyku durumları donanım gereksinimidir, optimizasyon değil. → [10](10-enerji-butcesi.md) |
| **K5** | Hareketli araç | Titreşim: konnektör tutma, ağır bileşen desteği, klemens tipi. Endüstriyel DIN pano varsayımında yoktu. |

**K1'in sonucu olan tasarım kuralı:** Node tarafında bir bileşenden tasarruf
etmek, host tarafında sekiz katı karmaşıklığa değer.

**K4'ün sonucu olan tasarım kuralı:** Sürekli açık kalan hiçbir bileşen
sorgulanmadan kabul edilmez. Bir fonksiyonun "her zaman hazır" olması, enerji
bütçesinde yerini hak ettiğini kanıtlamalıdır.

> **K4, K1 ile çatıştığında K4 kazanır.** Node'da bir uyku devresi için ek
> maliyet, batarya ömrü karşılığında kabul edilebilir.

## 4. Node tipleri · D-72

Katalog: [09 §5](09-node-aileleri.md#5-node-katalogu). Dil **node tipi**.
Form en fazla **2U** (D-75).

| SKU | U | Özet |
|-----|---|------|
| DI-8 | 1 | 8 giriş, **5–30 V izole** — ilk PCB (D-28, D-76) |
| DO-M-8A-8 | 1 | 8 × 8 A MOSFET, PWM var; 8 A röle yok |
| AI-8 | 1 | NTC / 4–20 / 0–20 mA / 0–10 V, port config |
| AO-4 | 1 | 0–10 V, ayrı node |
| DC-L-16A-4 | 1* | Latching 16 A |
| DC-H-32A-2 | 2 | Hibrit 32 A |
| DC-H-64A-2 | 2 | Hibrit 64 A, 48 V ESS |
| AC-L-16A-4 | 2 | AC 16 A ×4 (8ch 4U olmasın) |
| AC-L-32A-2 | 2 | AC 32 A ×2 |
| COM-1U | 1 | CAN + Ethernet |

## 5. Standardize edilmesi zorunlu kalemler

Aşağıdakiler **geriye dönük değiştirilemez**. Sonradan değişirse tüm node ailesi
yeniden tasarlanır. Bu yüzden ilk şema çizilmeden önce kilitlenmeleri gerekir.

| Kalem | Doküman | Neden geri dönülemez |
|-------|---------|----------------------|
| Mekanik slot yapısı, 1U/2U | [04 §2](04-backplane-mekanik.md#2-slot-ve-node-ölçüleri) | Kutu, backplane ve tüm node PCB'leri bağlı |
| Backplane pinout | [04 §5](04-backplane-mekanik.md#5-pinout) | Üretilmiş her node uyumsuz hale gelir |
| Konnektör ve mate sırası | [04 §4](04-backplane-mekanik.md#4-konnektör-seçimi) | **v1 canlı tak-çıkar (D-24)** — sonradan eklenemez |
| Güç dağıtımı ve rail tanımı | [03 §2](03-guc-mimarisi.md#2-rail-topolojisi) | Node regülatör tasarımı bağlı |
| Dahili protokol ve fiziksel katman | [05 §1](05-dahili-bus.md#1-fiziksel-katman-kararı) | Sahadaki node'ların firmware'i bağlı |
| Slot adresleme | [06 §1](06-slot-yonetimi.md#1-slot-adresleme) | Saha servis prosedürü bağlı |
| Discovery ve descriptor formatı | [06 §8](06-slot-yonetimi.md#8-discovery-akışı) | Geriye uyumluluk için versiyon alanı şart |
| Bootloader protokolü | [07](07-firmware-update.md) | Sahadaki node'lar güncellenemez hale gelir |
| Node uyku/uyanma sözleşmesi | [10 §3](10-enerji-butcesi.md#3-wake-on-bus-nodeların-uyuması) | Host ile node'un uyku beklentisi uyuşmazsa cevapsız kalır |
| Node tutma mekanizması | [04 §3.3](04-backplane-mekanik.md#33-takma--çıkarma) | **Kapalı vida (D-45)** — sonradan eklenemez |

**Uygulanan koruma:** Descriptor'ın ilk baytı **protokol versiyonudur**. Host,
tanımadığı bir versiyonu gördüğünde node'u devre dışı bırakır ama rafı düşürmez.
Bu, ileride sözleşmeyi kontrollü biçimde kırabilmek için bırakılan tek kapıdır.

## 6. Kapsam dışı (şimdilik)

Karışıklığı önlemek için açıkça belirtiliyor:

- Fonksiyonel güvenlik (SIL / PL) iddiası yok
- Redundant host / yüksek erişilebilirlik yok
- Motion control / gerçek zamanlı senkron eksen kontrolü yok
- EtherCAT, PROFINET gibi endüstriyel gerçek zamanlı Ethernet protokolleri yok
