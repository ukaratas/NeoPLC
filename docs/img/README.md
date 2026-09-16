# Görseller

Mimari kararların görsel karşılıkları. Hepsi **SVG** — GitHub'da doğrudan
render oluyor, versiyonlanabiliyor, metin tabanlı olduğu için diff'i okunabilir.

> ⚠️ Bu görseller **mimari karar seviyesindedir**, üretim çizimi değildir.
> Ölçüler karar kütüğündeki değerleri yansıtır; mekanik toleranslar, malzeme
> kalınlıkları ve montaj detayları CAD aşamasında netleşecek.

---

| # | Görsel | Neyi gösteriyor | İlgili doküman |
|---|--------|-----------------|----------------|
| 01 | [Sistem ön görünüm](01-sistem-onden.svg) | 8 slot, karışık 1U/2U yerleşim, host bölümü, ölçüler | [01](../01-sistem-genel-bakis.md) |
| 02 | [Blade şasi üstten kesit](02-blade-kizak-kesit.svg) | Kızak rayları, backplane, takma yönü, oluk detayı | [04 §1](../04-backplane-mekanik.md), [04 §3](../04-backplane-mekanik.md) |
| 03 | [1U node anatomisi](03-node-1u-anatomi.svg) | Çıplak PCB + ön panel, bileşen yerleşimi, yükseklik bütçesi | [04 §2](../04-backplane-mekanik.md) |
| 04 | [Kart kenarı stagger](04-kartkenari-stagger.svg) | 26 pin, 4 kademeli mate sırası, pin dizilimi | [04 §5](../04-backplane-mekanik.md) |
| 05 | [Hava akışı](05-hava-akisi.svg) | Blade kanalları, fan, debi hesabı | [04 §6](../04-backplane-mekanik.md) |

---

## Renk kodu

Tüm görsellerde tutarlı:

| Renk | Anlam |
|------|-------|
| 🟩 Yeşil `#2d6a4f` | PCB |
| 🟨 Altın `#c9a227` | Kart kenarı gold finger |
| 🟦 Mavi `#3d5a80` | 1U DC node ön paneli · host |
| 🟪 Mor `#4a3f5c` | 2U AC node (şebeke) |
| 🟫 Kahve `#5c4033` | 2U güç node'u (yüksek akım) |
| 🟧 Turuncu `#bf5b25` | Dikkat / hareket / sıcak hava |
| 🔵 Açık mavi `#4a7fb5` | Soğuk hava / fan |
| ⬜ Bej `#d8d3c8` | Kızak rayı / mekanik |

## Düzenleme

SVG'ler elle yazıldı, bir çizim aracından export edilmedi — doğrudan metin
editöründe düzenlenebilir. Karar değişince ilgili görsel de güncellenmeli.

Yerelde PNG önizleme:

```bash
qlmanage -t -s 1400 -o /tmp/png docs/img/*.svg
```
