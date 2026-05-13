# Official API Notes

Source material:

- Official ASP.NET Help page: `https://broadair.remotcon.mobi/Help`
- Official Android package `jmg.comcom.yuanda.yuanda` version 6.7
- Live verification with a real BROAD AIR account on 2026-05-13

## Base URL

The public Help page is hosted at:

```text
https://broadair.remotcon.mobi
```

The Android app uses:

```text
https://broadcleanair.net:8103
```

The latter is the endpoint that successfully authenticated during live testing. The certificate served by that host does not currently match `broadcleanair.net`, so clients may need to disable SSL verification or provide a custom trust strategy.

## Login

Endpoint:

```text
POST /api/Account/Login
```

Payload:

```json
{
  "user_id": "<phone-or-user-id>",
  "pass_word": "<password>",
  "token": "8q7l82AxXB8Qo99vesUUvy1ED5tIuPT31NoIL6ZE5THH7clkfN",
  "nonce": "<six digits>",
  "timestamp": "<unix seconds>",
  "sign": "md5(token + nonce + timestamp)"
}
```

The returned `Body.Data.token` is the session token used as a `token` request header for subsequent calls.

## Fresh Air Device List

Endpoint:

```text
POST /api/Equipment/GetEquipmentsList
```

Headers:

```text
token: <session-token>
```

Payload:

```json
{
  "user_id": "<user-id>",
  "eqType": "02",
  "pageIndex": "1",
  "pageSize": "10"
}
```

`eqType` values observed in the app:

- `01`: air quality monitor
- `02`: fresh air unit
- `03`: portable fresh lung device

The response wraps `Body.Data` as a JSON-encoded string.

## Fresh Air Status

Endpoint:

```text
POST /api/Equipment/GetFreshAirStatus
```

Headers:

```text
token: <session-token>
```

Payload:

```json
{
  "user_id": "<user-id>",
  "eq_guid": "<device-guid>",
  "eq_name": "",
  "city": "",
  "pageIndex": "1",
  "pageSize": "10",
  "codeinfo": "",
  "time": "<unix-ms>"
}
```

The response wraps `Body.Data` as a JSON-encoded object. Useful fields observed during live verification include:

- `TEMP_INDOOR1`
- `TEMP_INDOOR2`
- `TEMP_OUTDOOR`
- `TEMP_FAIR`
- `TEMP_EXHAUST`
- `SUPPLY_AIR_TEMP`
- `INDOOR_HUMIDITY`
- `SUPPLY_AIR_HUMIDITY`
- `CO2_CONCENTRATION`
- `OUT_PM2.5`
- `PATICLE_CCT_2_5`
- `RT_VOLUME`
- `FREQUENCY_RUN`
- `FREQUENCY_SET`
- `POWER_USED_RT`
- `RT_HOT_RECOVERY`
- `FAULT`

## Control API For Phase 2

Endpoint:

```text
POST /api/Equipment/SetFreshAir
```

Payload:

```json
{
  "eq_guid": "<device-guid>",
  "sjx": "<operation>",
  "cs": "<value>"
}
```

Operations observed in the official app:

- `1`: get realtime data; `cs` is the current timestamp in milliseconds
- `2`: power off
- `3`: power on
- `4`: set frequency / manual mode
- `20`: update automatic tuning configuration
- `23`: enable automatic CO2/freshness tuning path

Control is intentionally deferred because it changes device state and needs more guardrails and live review.
