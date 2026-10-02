# Vibrix PureFlow voor Home Assistant

Deze custom integration bedient een Vibrix PureFlow15 rechtstreeks via het lokale netwerk. Nadat de lokale sleutel bekend is, gebruikt de integratie geen Tuya-cloud voor statusupdates of opdrachten.

De PureFlow15 is een Tuya-OEM-apparaat. Met de standaardfirmware kan de Tuya-techniek daarom niet volledig worden verwijderd: de eerste activatie en het opvragen van de lokale sleutel lopen normaal gesproken eenmalig via Tuya. Daarna kun je internettoegang voor de luchtreiniger blokkeren, zolang Home Assistant hem op het LAN kan blijven bereiken.

## Ondersteunde Home Assistant-entiteiten

- Luchtreiniger als `fan`, inclusief aan/uit, `low`, `mid`, `high`, `turbo` en auto-/slaapmodus.
- PM2.5, VOC, luchtkwaliteit en resterende filterlevensduur als sensoren.
- Ionisator, kinderslot en display als schakelaars.
- Uitschakeltimer van één tot vijf uur en een knop om de filterlevensduur te resetten.
- Configuratie volledig via de Home Assistant-interface.
- Diagnostiek met actuele datapoints; IP-adres, device-ID en lokale sleutel worden geredigeerd.

## Benodigd

- Home Assistant 2026.7 of nieuwer.
- Een PureFlow15 die op hetzelfde lokale netwerk zit als Home Assistant.
- Een vast of gereserveerd IP-adres voor de luchtreiniger.
- Het Tuya `device_id`, de lokale sleutel van 16 tekens en protocolversie 3.1 t/m 3.5.

TinyTuya documenteert de actuele procedure om de sleutel via de Tuya IoT-portal op te halen: <https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys>. De netwerkscan toont het IP-adres, device-ID en de protocolversie:

```text
python -m pip install tinytuya==1.20.0
python -m tinytuya scan
python -m tinytuya wizard
```

Geeft de wizard op Windows `CERTIFICATE_VERIFY_FAILED`, laat Python dan de
Windows-certificaatopslag gebruiken en start de wizard opnieuw:

```text
python -m pip install pip-system-certs
python -m tinytuya wizard
```

Bewaar `devices.json`, `tinytuya.json` en `tuya-raw.json` niet in Git: ze bevatten geheime sleutels en staan daarom in `.gitignore`.

## Installatie

### Handmatig

1. Kopieer `custom_components/vibrix_pureflow` naar `/config/custom_components/vibrix_pureflow` op Home Assistant.
2. Herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**.
4. Zoek naar **Vibrix PureFlow**.

### HACS custom repository

1. Open **HACS** in de zijbalk van Home Assistant.
2. Open rechtsboven het menu met de drie puntjes en kies **Custom repositories**.
3. Voeg `https://github.com/Cindyst1/vibrix-pureflow-home-assistant` toe
   als type **Integration**.
4. Open **Vibrix PureFlow** in HACS en kies **Download**.
5. Herstart Home Assistant.
6. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen** en
   zoek naar **Vibrix PureFlow**.

## Datapoints bepalen

Voor de geteste PureFlow15 Pro met protocol 3.5 zijn de datapoints:

| DP | Functie | Waarden |
| --- | --- | --- |
| 1 | Aan/uit | `true`, `false` |
| 2 | PM2.5 | 0–999 µg/m³ |
| 3 | Modus/snelheid | `auto`, `sleep`, `low`, `mid`, `high`, `turbo` |
| 5 | Filterlevensduur | 0–100% |
| 6 | Ionisator | `true`, `false` |
| 7 | Kinderslot | `true`, `false` |
| 8 | Display | `true`, `false` |
| 11 | Filterreset | puls naar `true` |
| 18 | Uitschakeltimer | `cancel`, `1h`, `2h`, `3h`, `4h`, `5h` |

De configuratie vult dit profiel automatisch in wanneer deze datapoints worden
gedetecteerd. Controleer de waarden bij andere hardware- of firmwarevarianten.

Tuya kent aan functies nummers toe die per hardware- of firmwarevariant kunnen verschillen. De configuratie toont alle datapoints die jouw apparaat rapporteert. Gebruik `tools/probe.py` om exact te bepalen welk nummer bij welke knop hoort:

```text
python tools/probe.py --ip 192.168.1.50 --id JOUW_DEVICE_ID --version 3.3
```

Na de TinyTuya-wizard kan de probe de sleutel rechtstreeks en zonder uitvoer
uit `devices.json` lezen:

```text
python tools/probe.py --device-file devices.json --name PureFlow15Pro
```

De lokale sleutel wordt veilig via een verborgen prompt gevraagd. Noteer eerst de beginsituatie, wijzig daarna telkens precies één functie op het fysieke bedieningspaneel en druk op Enter. De probe toont alleen de gewijzigde datapoints.

Voorbeeld van mogelijke snelheidswaarden:

```text
level_1, level_2, level_3, level_4
```

Of, wanneer het apparaat getallen gebruikt:

```text
1, 2, 3, 4
```

Selecteer onbekende datapoints niet. Een verkeerde sensorselectie is vooral verwarrend; een verkeerd schakel-datapoint kan een andere apparaatfunctie bedienen.

## Na de configuratie

Als lokale bediening betrouwbaar werkt, kun je in je router internettoegang voor de luchtreiniger blokkeren. Laat verkeer tussen Home Assistant en het apparaat op het lokale netwerk toe, waaronder TCP-poort 6668. Na een fabrieksreset of opnieuw koppelen verandert de lokale sleutel; gebruik dan **Herconfigureren** bij de integratie om de nieuwe sleutel in te voeren.

## Beperking zonder Tuya

Volledig zonder ooit een Tuya-app of -account te gebruiken is met de standaardfirmware waarschijnlijk niet mogelijk: Tuya-apparaten moeten eerst worden geactiveerd en de lokale sleutel is nodig voor versleutelde LAN-communicatie. De enige echte Tuya-vrije route is alternatieve firmware op de wifi-module, waarvoor het exacte module- en printplaattype onderzocht moet worden en waarbij schade of verlies van garantie mogelijk is.
