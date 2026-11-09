# Vibrix PureFlow voor Home Assistant

[English](README.md) | [Nederlands](README_NL.md)

Een onofficiële Home Assistant custom integratie waarmee je een Vibrix PureFlow15 rechtstreeks via het lokale netwerk bedient.

Nadat de lokale sleutel is opgehaald, verlopen statusupdates en opdrachten lokaal zonder gebruik van de Tuya-cloud. De luchtreiniger moet vanaf Home Assistant bereikbaar blijven op hetzelfde lokale netwerk.

> [!IMPORTANT]
> De PureFlow15 is een Tuya OEM-apparaat. Met de originele firmware is Tuya doorgaans eenmalig nodig voor de eerste activatie en het ophalen van de lokale sleutel. Daarna kun je de internettoegang van de luchtreiniger blokkeren, zolang lokaal netwerkverkeer mogelijk blijft.

## Functies

- Lokale bediening vanuit Home Assistant via het Tuya LAN-protocol.
- Aan/uit en ventilatorstanden `low`, `mid`, `high` en `turbo`.
- Automatische stand en slaapstand.
- Sensoren voor PM2.5, VOC, luchtkwaliteit en resterende filterlevensduur wanneer het apparaat deze ondersteunt.
- Schakelaars voor ionisator, kinderslot en display.
- Uitschakeltimer van één tot vijf uur.
- Knop om de filterlevensduur te resetten.
- Volledige configuratie via de Home Assistant-interface.
- Diagnostiek waarin gevoelige waarden zoals IP-adres, device-ID en lokale sleutel worden afgeschermd.

## Benodigdheden

- Home Assistant 2026.7 of nieuwer.
- Een Vibrix PureFlow15 op hetzelfde lokale netwerk als Home Assistant.
- Een vast of via DHCP gereserveerd IP-adres voor de luchtreiniger.
- De Tuya device-ID.
- De lokale sleutel van 16 tekens.
- Tuya-protocolversie 3.1 tot en met 3.5.

## Apparaatgegevens ophalen

TinyTuya beschrijft de actuele procedure om lokale sleutels via het Tuya IoT Platform op te halen: [TinyTuya setup wizard](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys).

Installeer TinyTuya en start de scanner en wizard:

```powershell
python -m pip install tinytuya==1.20.0
python -m tinytuya scan
python -m tinytuya wizard
```

De scan toont het IP-adres, de device-ID en de protocolversie van de luchtreiniger. De wizard maakt `devices.json` aan; daarin staat de lokale sleutel.

Geeft de wizard op Windows `CERTIFICATE_VERIFY_FAILED`, installeer dan ondersteuning voor de Windows-certificaatopslag en probeer het opnieuw:

```powershell
python -m pip install pip-system-certs
python -m tinytuya wizard
```

> [!WARNING]
> Publiceer `devices.json`, `tinytuya.json` en `tuya-raw.json` nooit. Deze bestanden kunnen accountgegevens en apparaatsleutels bevatten. Ze zijn daarom uitgesloten via de `.gitignore` van deze repository.

## Installatie

### HACS custom repository

1. Open **HACS** in Home Assistant.
2. Open rechtsboven het menu en kies **Custom repositories**.
3. Voeg `https://github.com/Cindyst1/vibrix-pureflow-home-assistant` toe.
4. Selecteer **Integration** als repositorytype.
5. Open **Vibrix PureFlow** in HACS en kies **Download**.
6. Herstart Home Assistant.
7. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**.
8. Zoek naar **Vibrix PureFlow**.

### Handmatige installatie

1. Kopieer `custom_components/vibrix_pureflow` naar `/config/custom_components/vibrix_pureflow` op Home Assistant.
2. Herstart Home Assistant.
3. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**.
4. Zoek naar **Vibrix PureFlow**.

## Configuratie

Vul tijdens de installatie het volgende in:

- Een naam voor de luchtreiniger.
- Het vaste IP-adres.
- De Tuya device-ID.
- De lokale sleutel van 16 tekens.
- De gevonden Tuya-protocolversie.

Sluit de Tuya- of Smart Life-app volledig voordat je de verbinding test. Sommige apparaten accepteren maar één actieve lokale verbinding tegelijk.

De integratie leest de beschikbare datapoints en vraagt daarna om de ondersteunde functies te koppelen. Selecteer alleen datapoints waarvan je de functie kent.

## Geteste datapoints van de PureFlow15 Pro

De geteste PureFlow15 Pro met protocol 3.5 rapporteert de volgende datapoints:

| DP | Functie | Waarden |
| --- | --- | --- |
| 1 | Aan/uit | `true`, `false` |
| 2 | PM2.5 | 0–999 µg/m³ |
| 3 | Modus/snelheid | `auto`, `sleep`, `low`, `mid`, `high`, `turbo` |
| 5 | Filterlevensduur | 0–100% |
| 6 | Ionisator | `true`, `false` |
| 7 | Kinderslot | `true`, `false` |
| 8 | Display | `true`, `false` |
| 11 | Filterreset | Puls naar `true` |
| 18 | Uitschakeltimer | `cancel`, `1h`, `2h`, `3h`, `4h`, `5h` |

Dit profiel wordt automatisch ingevuld wanneer deze datapoints worden gevonden. Datapointnummers en waarden kunnen per hardware- of firmwareversie verschillen.

## Onbekende datapoints bepalen

Gebruik `tools/probe.py` om wijzigingen in datapoints te vergelijken terwijl je steeds één functie op de luchtreiniger bedient:

```powershell
python tools/probe.py --ip 192.168.1.50 --id JOUW_DEVICE_ID --version 3.5
```

Na het uitvoeren van de TinyTuya-wizard kan de probe de sleutel veilig uit `devices.json` lezen zonder hem weer te geven:

```powershell
python tools/probe.py --device-file devices.json --name PureFlow15Pro
```

Noteer de beginsituatie, wijzig precies één functie op het fysieke bedieningspaneel en druk op Enter. De probe toont alleen de datapoints die zijn veranderd.

Koppel geen onbekende schakel-datapoints. Een verkeerde sensorkoppeling geeft verwarrende meetwaarden; een verkeerde schakelkoppeling kan een andere apparaatfunctie bedienen.

## Alleen lokaal gebruiken

Wanneer lokale bediening betrouwbaar werkt, kun je de internettoegang van de luchtreiniger in je router blokkeren. Laat verkeer tussen Home Assistant en de luchtreiniger op het lokale netwerk toe, waaronder TCP-poort 6668.

Reserveer het IP-adres van de luchtreiniger in je router, zodat de integratie hem altijd kan vinden. Na een fabrieksreset of opnieuw koppelen kan de lokale sleutel veranderen. Gebruik dan **Herconfigureren** bij de integratie om de nieuwe verbindingsgegevens in te voeren.

## Problemen oplossen

- **Geen verbinding:** controleer het IP-adres, de device-ID, lokale sleutel en protocolversie.
- **Apparaat wordt niet beschikbaar:** sluit de Tuya/Smart Life-app en controleer of Home Assistant de luchtreiniger via het LAN kan bereiken.
- **Verbinding stopt na een IP-wijziging:** maak een DHCP-reservering en herconfigureer de integratie met het huidige adres.
- **Authenticatie mislukt na opnieuw koppelen:** haal de nieuwe lokale sleutel op en herconfigureer de integratie.
- **Een functie werkt verkeerd:** controleer het datapoint met `tools/probe.py` en pas de koppeling aan.

## Beperking van Tuya

Met de originele firmware is gebruik zonder ooit een Tuya-app of -account te gebruiken doorgaans niet mogelijk. Het apparaat moet eerst worden geactiveerd en de lokale sleutel is nodig voor versleutelde LAN-communicatie.

De enige volledig Tuya-vrije route is geschikte alternatieve firmware voor exact dezelfde wifi-module en printplaatversie. Hiervoor is hardwareonderzoek nodig en het kan het apparaat beschadigen of de garantie laten vervallen.

## Ondersteuning

Een probleem gevonden of gebruikt jouw PureFlow andere datapoints? [Open een issue](https://github.com/Cindyst1/vibrix-pureflow-home-assistant/issues) en vermeld de Home Assistant-versie, integratieversie, protocolversie en afgeschermde diagnostiek. Deel nooit je lokale sleutel.
