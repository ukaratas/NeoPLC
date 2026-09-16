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
│  │ ESP32-S3 + W5500 · Güç katı · Slot yönetimi            │  │
│  └────────────────────────────────────────────────────────┘  │
│  ═══════════════════ BACKPLANE (8 slot) ═══════════════════  │
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

Node slotu **tüketmez**. Node'ları barındıran, besleyen, yöneten ve dış dünya
ile haberleştiren ana platformdur.

Sorumlulukları:

- 12–48V giriş koruması ve sistem güç üretimi
- 8 slotun beslenmesi, güç bütçesi zorlaması, arıza izolasyonu
- Node discovery, konfigürasyon, sağlık takibi
- Dahili bus yöneticiliği (deterministik tarama)
- Dış haberleşme: Ethernet / Modbus TCP, RS-485 / Modbus RTU, Wi-Fi
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
| **K1** | 8 slot × düşük maliyetli node | Node elektroniği ucuz ve az pinli olmalı. Karmaşıklık host'a yığılır — orada bir kez ödenir, node'da sekiz kez. |
| **K2** | 12–48V geniş giriş | 48V nominal → transient sonrası ~90V. Ön kat gerilim sınıfını bu belirliyor, dolayısıyla parça maliyetini ve tedarik edilebilirliğini. |
| **K3** | 2 katman tercihi | Kontrollü empedans ve RMII 50MHz pratikte elenir. Bu, doğrudan MCU ve Ethernet kontrolcüsü seçimini değiştiriyor. |
| **K4** | **Batarya beslemesi — enerji bütçesi** | **Boşta tüketim ürünün yaşayabilirliğini belirliyor.** Sürekli çalışan her bileşen sorgulanır; uyku durumları donanım gereksinimidir, optimizasyon değil. → [10](10-enerji-butcesi.md) |
| **K5** | Hareketli araç | Titreşim: konnektör tutma, ağır bileşen desteği, klemens tipi. Endüstriyel DIN pano varsayımında yoktu. |

**K1'in sonucu olan tasarım kuralı:** Node tarafında bir bileşenden tasarruf
etmek, host tarafında sekiz katı karmaşıklığa değer.

**K4'ün sonucu olan tasarım kuralı:** Sürekli açık kalan hiçbir bileşen
sorgulanmadan kabul edilmez. Bir fonksiyonun "her zaman hazır" olması, enerji
bütçesinde yerini hak ettiğini kanıtlamalıdır.

> **K4, K1 ile çatıştığında K4 kazanır.** Node'da bir uyku devresi için ek
> maliyet, batarya ömrü karşılığında kabul edilebilir.

## 4. Node aileleri (hedef)

| Aile | Form | Öncelik |
|------|------|---------|
| Dijital giriş | 1U | Faz 1 |
| Dijital çıkış | 1U | Faz 1 |
| Röle çıkış | 1U / 2U | Faz 2 |
| Analog giriş | 1U / 2U | Faz 2 |
| Analog çıkış | 1U / 2U | Faz 2 |
| Haberleşme | 1U / 2U | Faz 3 |
| Özel fonksiyon | 1U / 2U | Faz 3 |

Ayrıntı: [09 — Node Aileleri](09-node-aileleri.md)

## 5. Standardize edilmesi zorunlu kalemler

Aşağıdakiler **geriye dönük değiştirilemez**. Sonradan değişirse tüm node ailesi
yeniden tasarlanır. Bu yüzden ilk şema çizilmeden önce kilitlenmeleri gerekir.

| Kalem | Doküman | Neden geri dönülemez |
|-------|---------|----------------------|
| Mekanik slot yapısı, 1U/2U | [04 §2](04-backplane-mekanik.md#2-slot-ve-node-ölçüleri) | Kutu, backplane ve tüm node PCB'leri bağlı |
| Backplane pinout | [04 §5](04-backplane-mekanik.md#5-pinout) | Üretilmiş her node uyumsuz hale gelir |
| Konnektör ve mate sırası | [04 §4](04-backplane-mekanik.md#4-konnektör-seçimi) | Hot-plug yeteneği sonradan eklenemez |
| Güç dağıtımı ve rail tanımı | [03](03-guc-mimarisi.md) | Node regülatör tasarımı bağlı |
| Dahili protokol ve fiziksel katman | [05](05-dahili-bus.md) | Sahadaki node'ların firmware'i bağlı |
| Slot adresleme | [06](06-slot-yonetimi.md) | Saha servis prosedürü bağlı |
| Discovery ve descriptor formatı | [06](06-slot-yonetimi.md) | Geriye uyumluluk için versiyon alanı şart |
| Bootloader protokolü | [07](07-firmware-update.md) | Sahadaki node'lar güncellenemez hale gelir |
| Node uyku/uyanma sözleşmesi | [10 §3](10-enerji-butcesi.md#3-wake-on-bus-nodeların-uyuması) | Host ile node'un uyku beklentisi uyuşmazsa cevapsız kalır |
| Node tutma mekanizması | [10 §9.3](10-enerji-butcesi.md#93-titreşim) | Mekanik standart — sonradan eklenemez |

**Uygulanan koruma:** Descriptor'ın ilk baytı **protokol versiyonudur**. Host,
tanımadığı bir versiyonu gördüğünde node'u devre dışı bırakır ama rafı düşürmez.
Bu, ileride sözleşmeyi kontrollü biçimde kırabilmek için bırakılan tek kapıdır.

## 6. Kapsam dışı (şimdilik)

Karışıklığı önlemek için açıkça belirtiliyor:

- Fonksiyonel güvenlik (SIL / PL) iddiası yok
- Redundant host / yüksek erişilebilirlik yok
- Motion control / gerçek zamanlı senkron eksen kontrolü yok
- EtherCAT, PROFINET gibi endüstriyel gerçek zamanlı Ethernet protokolleri yok
