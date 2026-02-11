/**
 * Nürnberger Uhr (Nuremberg Clock) - Subjective Day Calculator
 * 
 * JavaScript implementation for client-side use (GitHub Pages compatible).
 * Calculates "subjective time" based on the historical unequal hours system.
 * 
 * Historical Background:
 * - Used in Nuremberg and other medieval cities
 * - Day is divided into 12 equal "day hours" (sunrise to sunset)
 * - Night is divided into 12 equal "night hours" (sunset to sunrise)
 * - Hour length varies throughout the year
 * 
 * Usage:
 *   const calculator = new SubjectiveDay(50.3167, 11.9167);  // Hof, Germany
 *   const result = calculator.getSubjectiveTime();
 *   console.log(result.display_en);  // "2nd hour of night (75.4 min/hr)"
 * 
 * References:
 * - https://de.wikipedia.org/wiki/Nürnberger_Uhr
 */

class SubjectiveDay {
    /**
     * Initialize the Subjective Day calculator.
     * @param {number} lat - Latitude in decimal degrees (-90 to 90)
     * @param {number} lon - Longitude in decimal degrees (-180 to 180)
     * @param {number|null} tzOffsetHours - Timezone offset from UTC (auto-detected if null)
     */
    constructor(lat, lon, tzOffsetHours = null) {
        if (lat < -90 || lat > 90) {
            throw new Error(`Latitude must be between -90 and 90, got ${lat}`);
        }
        if (lon < -180 || lon > 180) {
            throw new Error(`Longitude must be between -180 and 180, got ${lon}`);
        }
        
        this.lat = lat;
        this.lon = lon;
        this._lastPolarType = null;
        
        if (tzOffsetHours === null) {
            // Auto-detect timezone offset for Central European Time
            this.tzOffsetHours = this._getCETOffset(new Date());
        } else {
            this.tzOffsetHours = tzOffsetHours;
        }
    }
    
    /**
     * Get Central European Time offset for a given date.
     * European DST: last Sunday of March to last Sunday of October.
     * @param {Date} date - Date to check
     * @returns {number} 1 for CET (winter), 2 for CEST (summer)
     */
    _getCETOffset(date) {
        const year = date.getFullYear();
        
        // Find last Sunday of March
        const marchLastDay = new Date(year, 2, 31);
        const marchLastSunday = new Date(year, 2, 31 - ((marchLastDay.getDay() + 1) % 7));
        marchLastSunday.setHours(2, 0, 0, 0);
        
        // Find last Sunday of October
        const octoberLastDay = new Date(year, 9, 31);
        const octoberLastSunday = new Date(year, 9, 31 - ((octoberLastDay.getDay() + 1) % 7));
        octoberLastSunday.setHours(3, 0, 0, 0);
        
        // Check if in DST period
        if (date >= marchLastSunday && date < octoberLastSunday) {
            return 2;  // CEST (summer time)
        }
        return 1;  // CET (winter time)
    }
    
    /**
     * Calculate Julian Day Number from Date.
     * @param {Date} date - Date object
     * @returns {number} Julian Day Number
     */
    _calculateJulianDay(date) {
        let year = date.getFullYear();
        let month = date.getMonth() + 1;
        const day = date.getDate() + date.getHours() / 24 + date.getMinutes() / 1440 + date.getSeconds() / 86400;
        
        if (month <= 2) {
            year -= 1;
            month += 12;
        }
        
        const a = Math.floor(year / 100);
        const b = 2 - a + Math.floor(a / 4);
        
        return Math.floor(365.25 * (year + 4716)) + Math.floor(30.6001 * (month + 1)) + day + b - 1524.5;
    }
    
    /**
     * Calculate sun declination and equation of time.
     * @param {number} jd - Julian Day Number
     * @returns {Object} {declination, eot}
     */
    _calculateSunPosition(jd) {
        const DEG_TO_RAD = Math.PI / 180;
        const RAD_TO_DEG = 180 / Math.PI;
        
        // Days since J2000.0
        const n = jd - 2451545.0;
        
        // Mean solar longitude (degrees)
        let L = (280.460 + 0.9856474 * n) % 360;
        if (L < 0) L += 360;
        
        // Mean anomaly (degrees)
        let g = (357.528 + 0.9856003 * n) % 360;
        if (g < 0) g += 360;
        const gRad = g * DEG_TO_RAD;
        
        // Ecliptic longitude (degrees)
        const lambdaSun = L + 1.915 * Math.sin(gRad) + 0.020 * Math.sin(2 * gRad);
        
        // Obliquity of ecliptic (degrees)
        const epsilon = 23.439 - 0.0000004 * n;
        const epsilonRad = epsilon * DEG_TO_RAD;
        
        // Solar declination
        const lambdaRad = lambdaSun * DEG_TO_RAD;
        const declination = Math.asin(Math.sin(epsilonRad) * Math.sin(lambdaRad)) * RAD_TO_DEG;
        
        // Equation of time (minutes)
        const y = Math.tan(epsilonRad / 2) ** 2;
        const LRad = L * DEG_TO_RAD;
        const eot = 4 * RAD_TO_DEG * (
            y * Math.sin(2 * LRad)
            - 2 * 0.01671 * Math.sin(gRad)
            + 4 * 0.01671 * y * Math.sin(gRad) * Math.cos(2 * LRad)
            - 0.5 * y * y * Math.sin(4 * LRad)
            - 1.25 * 0.01671 * 0.01671 * Math.sin(2 * gRad)
        );
        
        return { declination, eot };
    }
    
    /**
     * Calculate sunrise and sunset times for a given date.
     * @param {Date} date - Date to calculate for
     * @returns {Object} {sunrise: Date, sunset: Date} or null values for polar regions
     */
    _calculateSunriseSunset(date) {
        const DEG_TO_RAD = Math.PI / 180;
        const RAD_TO_DEG = 180 / Math.PI;
        
        // Use noon on the given day for calculation
        const noon = new Date(date);
        noon.setHours(12, 0, 0, 0);
        const jd = this._calculateJulianDay(noon);
        
        // Get sun position
        const { declination, eot } = this._calculateSunPosition(jd);
        
        // Hour angle at sunrise/sunset (degrees)
        // Using standard refraction of -0.833 degrees
        const latRad = this.lat * DEG_TO_RAD;
        const declRad = declination * DEG_TO_RAD;
        
        const cosHourAngle = (Math.sin(-0.833 * DEG_TO_RAD) -
            Math.sin(latRad) * Math.sin(declRad)) /
            (Math.cos(latRad) * Math.cos(declRad));
        
        // Handle polar day/night
        if (cosHourAngle > 1) {
            // Polar night - sun never rises
            this._lastPolarType = 'night';
            return { sunrise: null, sunset: null };
        } else if (cosHourAngle < -1) {
            // Polar day - sun never sets
            this._lastPolarType = 'day';
            return { sunrise: null, sunset: null };
        }
        
        const hourAngle = Math.acos(cosHourAngle) * RAD_TO_DEG;
        
        // Solar noon (local time) in minutes from midnight
        const solarNoonMinutes = 720 - 4 * this.lon - eot + this.tzOffsetHours * 60;
        
        // Sunrise and sunset in minutes from midnight
        const sunriseMinutes = solarNoonMinutes - hourAngle * 4;
        const sunsetMinutes = solarNoonMinutes + hourAngle * 4;
        
        // Convert to Date objects
        const baseDate = new Date(date);
        baseDate.setHours(0, 0, 0, 0);
        
        const sunrise = new Date(baseDate.getTime() + sunriseMinutes * 60000);
        const sunset = new Date(baseDate.getTime() + sunsetMinutes * 60000);
        
        return { sunrise, sunset };
    }
    
    /**
     * Get sunrise and sunset times for a given date.
     * @param {Date|null} date - Date to calculate for (defaults to now)
     * @returns {Object} Sunrise/sunset information
     */
    getSunriseSunset(date = null) {
        if (date === null) {
            date = new Date();
        }
        
        const { sunrise, sunset } = this._calculateSunriseSunset(date);
        
        if (sunrise === null || sunset === null) {
            return {
                polar: true,
                polarType: this._lastPolarType,
                sunrise: null,
                sunset: null
            };
        }
        
        const dayLength = (sunset - sunrise) / 1000;  // seconds
        const nightLength = 86400 - dayLength;
        
        return {
            polar: false,
            sunrise: sunrise,
            sunset: sunset,
            dayLengthHours: dayLength / 3600,
            nightLengthHours: nightLength / 3600,
            dayHourLengthMinutes: (dayLength / 12) / 60,
            nightHourLengthMinutes: (nightLength / 12) / 60
        };
    }
    
    /**
     * Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)
     * @param {number} n - Number
     * @returns {string} Ordinal suffix
     */
    _getOrdinalSuffix(n) {
        if (n >= 11 && n <= 13) return 'th';
        switch (n % 10) {
            case 1: return 'st';
            case 2: return 'nd';
            case 3: return 'rd';
            default: return 'th';
        }
    }
    
    /**
     * Calculate the subjective time according to Nürnberger Uhr.
     * @param {Date|null} date - Datetime to calculate for (defaults to now)
     * @returns {Object} Subjective time information
     */
    getSubjectiveTime(date = null) {
        if (date === null) {
            date = new Date();
        }
        
        // Get today's sunrise and sunset
        const sunData = this.getSunriseSunset(date);
        
        if (sunData.polar) {
            return {
                polar: true,
                polarType: sunData.polarType,
                isDay: sunData.polarType === 'day',
                hour: 0,
                minute: 0,
                display: 'Polar ' + sunData.polarType,
                display_de: 'Polarer ' + (sunData.polarType === 'day' ? 'Tag' : 'Nacht'),
                display_en: 'Polar ' + sunData.polarType,
                timestamp: date.toISOString(),
                location: { lat: this.lat, lon: this.lon }
            };
        }
        
        const sunrise = sunData.sunrise;
        const sunset = sunData.sunset;
        
        // Get previous day's sunset and next day's sunrise for night calculation
        const yesterday = new Date(date);
        yesterday.setDate(yesterday.getDate() - 1);
        const tomorrow = new Date(date);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const yesterdayData = this._calculateSunriseSunset(yesterday);
        const tomorrowData = this._calculateSunriseSunset(tomorrow);
        
        let isDay, period, periodEn, hourLength, hour, minute;
        
        // Determine if it's day or night and calculate subjective hour
        if (date >= sunrise && date < sunset) {
            // Daytime
            isDay = true;
            period = 'Tag';
            periodEn = 'day';
            
            const dayLength = (sunset - sunrise) / 1000;  // seconds
            const elapsed = (date - sunrise) / 1000;
            
            hourLength = dayLength / 12;
            const hourFloat = elapsed / hourLength;
            hour = Math.floor(hourFloat) + 1;
            if (hour > 12) hour = 12;
            
            const minuteFraction = hourFloat - Math.floor(hourFloat);
            minute = Math.floor(minuteFraction * 60);
        } else {
            // Nighttime
            isDay = false;
            period = 'Nacht';
            periodEn = 'night';
            
            let nightStart, nightEnd;
            if (date >= sunset) {
                nightStart = sunset;
                nightEnd = tomorrowData.sunrise;
            } else {
                nightStart = yesterdayData.sunset;
                nightEnd = sunrise;
            }
            
            const nightLength = (nightEnd - nightStart) / 1000;
            const elapsed = (date - nightStart) / 1000;
            
            hourLength = nightLength / 12;
            const hourFloat = elapsed / hourLength;
            hour = Math.floor(hourFloat) + 1;
            if (hour > 12) hour = 12;
            
            const minuteFraction = hourFloat - Math.floor(hourFloat);
            minute = Math.floor(minuteFraction * 60);
        }
        
        const hourLengthMinutes = hourLength / 60;
        const ordinalSuffix = this._getOrdinalSuffix(hour);
        
        return {
            polar: false,
            isDay: isDay,
            hour: hour,
            minute: minute,
            hourLengthMinutes: Math.round(hourLengthMinutes * 100) / 100,
            period: period,
            periodEn: periodEn,
            display: `${hour}. Stunde des ${period}s`,
            display_de: `${hour}. Stunde des ${period}s (${hourLengthMinutes.toFixed(1)} min/Std)`,
            display_en: `${hour}${ordinalSuffix} hour of ${periodEn} (${hourLengthMinutes.toFixed(1)} min/hr)`,
            timeFormatted: `${hour}:${minute.toString().padStart(2, '0')}`,
            timestamp: date.toISOString(),
            location: { lat: this.lat, lon: this.lon },
            sunrise: sunrise.toTimeString().substring(0, 5),
            sunset: sunset.toTimeString().substring(0, 5),
            dayHourLengthMinutes: Math.round(sunData.dayHourLengthMinutes * 100) / 100,
            nightHourLengthMinutes: Math.round(sunData.nightHourLengthMinutes * 100) / 100
        };
    }
    
    /**
     * Get all 24 subjective hours for a given day.
     * @param {Date|null} date - Date to calculate for (defaults to today)
     * @returns {Object} Day and night hours
     */
    getFullDayHours(date = null) {
        if (date === null) {
            date = new Date();
        }
        
        const sunData = this.getSunriseSunset(date);
        
        if (sunData.polar) {
            return {
                polar: true,
                polarType: sunData.polarType,
                dayHours: [],
                nightHours: []
            };
        }
        
        const sunrise = sunData.sunrise;
        const sunset = sunData.sunset;
        
        // Get next day's sunrise for night hours
        const tomorrow = new Date(date);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowData = this._calculateSunriseSunset(tomorrow);
        
        // Calculate day hours
        const dayLength = (sunset - sunrise) / 1000;
        const dayHourLength = dayLength / 12;
        
        const dayHours = [];
        for (let i = 0; i < 12; i++) {
            const start = new Date(sunrise.getTime() + i * dayHourLength * 1000);
            const end = new Date(sunrise.getTime() + (i + 1) * dayHourLength * 1000);
            dayHours.push({
                hour: i + 1,
                start: start.toTimeString().substring(0, 8),
                end: end.toTimeString().substring(0, 8),
                lengthMinutes: Math.round(dayHourLength / 60 * 100) / 100
            });
        }
        
        // Calculate night hours
        const nightLength = (tomorrowData.sunrise - sunset) / 1000;
        const nightHourLength = nightLength / 12;
        
        const nightHours = [];
        for (let i = 0; i < 12; i++) {
            const start = new Date(sunset.getTime() + i * nightHourLength * 1000);
            const end = new Date(sunset.getTime() + (i + 1) * nightHourLength * 1000);
            nightHours.push({
                hour: i + 1,
                start: start.toTimeString().substring(0, 8),
                end: end.toTimeString().substring(0, 8),
                lengthMinutes: Math.round(nightHourLength / 60 * 100) / 100
            });
        }
        
        return {
            polar: false,
            date: date.toISOString().substring(0, 10),
            sunrise: sunrise.toTimeString().substring(0, 5),
            sunset: sunset.toTimeString().substring(0, 5),
            dayHours: dayHours,
            nightHours: nightHours,
            dayHourLengthMinutes: Math.round(dayHourLength / 60 * 100) / 100,
            nightHourLengthMinutes: Math.round(nightHourLength / 60 * 100) / 100
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SubjectiveDay;
}

// Make available globally for browser use
if (typeof window !== 'undefined') {
    window.SubjectiveDay = SubjectiveDay;
}
