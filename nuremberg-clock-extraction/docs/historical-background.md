# Historical Background: Die Nürnberger Uhr

## The Nuremberg Clock System

### Overview

The **Nürnberger Uhr** (Nuremberg Clock) was a unique timekeeping system used in Nuremberg, Germany from medieval times until the 19th century. It represents one of the most sophisticated pre-modern approaches to civil timekeeping, adapting to the natural rhythm of daylight hours.

### Terminology

| German | English | Description |
|--------|---------|-------------|
| **Große Uhr** | Great Clock | The seasonal hour system with variable day/night hour counts |
| **Kleine Uhr** | Small Clock | The standard 12-hour system (what we use today) |
| **Tagstunden** | Day Hours | Hours from sunrise to sunset |
| **Nachtstunden** | Night Hours | Hours from sunset to sunrise |
| **Wendetage** | Turning Days | 16 days per year when hour counts were adjusted |
| **Garaus** | Closing Signal | Horn signal at sunset for closing city gates |
| **Türmer** | Tower Watchman | Bell ringer who announced the hours |

### The Two Systems

#### Große Uhr (Historical Nuremberg System)

The true historical system varied the **number** of hours based on season:

| Season | Day Hours | Night Hours | Total |
|--------|-----------|-------------|-------|
| Winter Solstice | 8 | 16 | 24 |
| Spring Equinox | 12 | 12 | 24 |
| Summer Solstice | 16 | 8 | 24 |
| Autumn Equinox | 12 | 12 | 24 |

The hour length stayed roughly constant (~60 minutes), but the number of hours changed.

#### Kleine Uhr / Temporal Hours (Simplified System)

The more commonly implemented system (and what this software uses) keeps the **number** of hours constant (12 day + 12 night) but varies the **length**:

| Season | Day Hour Length | Night Hour Length |
|--------|-----------------|-------------------|
| Winter | ~40-45 min | ~75-80 min |
| Equinox | ~60 min | ~60 min |
| Summer | ~75-80 min | ~40-45 min |

This is the "temporal hours" system used throughout the ancient and medieval world.

### Historical Context

#### Origins

The temporal hour system dates back to ancient Egypt, Greece, and Rome. The Nuremberg adaptation was particularly sophisticated due to:

1. **Bell towers** - The city's tower watchmen (Türmer) announced hours
2. **Sundials** - Primary daytime timekeeping
3. **Water clocks** - Backup and nighttime use
4. **Star observations** - Nocturnal instruments used at night

#### Daily Life

Citizens organized their lives around this system:

- **Markets** opened at specific subjective hours
- **City gates** closed at sunset (Garaus)
- **Work hours** were defined by daylight
- **Church services** followed the canonical hours

#### The Wendetage

Sixteen "turning days" per year were designated for adjusting the hour counts:

1. The Türmer would announce a different number of hours
2. City bells would ring a new pattern
3. Citizens adjusted their activities accordingly

These fell roughly every 23 days, aligned with the calendar.

### The Tower Watchmen (Türmer)

The Türmer were crucial to the system's operation:

1. **Day duties**: Observed sundials, rang bells on the hour
2. **Night duties**: Used nocturnal instruments and star observations
3. **Emergency duties**: Watch for fires, sound alarms

They lived in the tower and were among the most important city employees.

### Transition to Modern Time

The Nürnberger Uhr persisted longer than in most European cities:

- **1806**: End of the Holy Roman Empire
- **1835**: First German railway (Nuremberg-Fürth) required standardized time
- **Late 19th century**: Complete transition to equal hours

Railway schedules made temporal hours impractical, and the system faded.

### Mathematical Basis

#### Solar Position

The system requires accurate sunrise/sunset calculations:

```
Hour Angle = arccos((sin(-0.833°) - sin(lat) × sin(declination)) / (cos(lat) × cos(declination)))
```

Where -0.833° accounts for atmospheric refraction.

#### Temporal Hour Length

```
Day Hour Length = (Sunset - Sunrise) / 12
Night Hour Length = (Next Sunrise - Sunset) / 12
```

#### Example (Nuremberg, Winter Solstice)

- Sunrise: 8:00
- Sunset: 16:00
- Day length: 8 hours (480 minutes)
- Day hour: 480 ÷ 12 = 40 minutes

### Cultural Significance

The Nürnberger Uhr represents:

1. **Adaptation to nature** - Time followed the sun, not machines
2. **Local identity** - Nuremberg's unique civic tradition
3. **Medieval technology** - Sophisticated for its era
4. **Social organization** - Structured daily life

### References

- Nicolai, Friedrich (1783): *Beschreibung einer Reise durch Deutschland*
- https://de.wikipedia.org/wiki/Nürnberger_Uhr
- https://nuernberginfos.de/nuernberg-mix/nuernberger-uhr.php
- https://www.chemie-schule.de/KnowHow/Nürnberger_Uhr
- Dohrn-van Rossum, Gerhard (1996): *Die Geschichte der Stunde*
