"""Solar geometry used by the rotation analysis - plain trigonometry, checkable by hand.

sun_ephemeris()   B0 (tilt of the Sun's axis toward Earth), L0 (Carrington longitude of the
                  disk centre) and P, from J. Meeus, Astronomical Algorithms (2nd ed.), ch. 25 & 29.
pixel_to_helio()  position on a solar image -> heliographic latitude and central-meridian distance.
fit_line()        straight-line fit used to turn positions over several days into a rotation rate.
"""
import numpy as np

CARRINGTON_RATE = 360 / 25.38   # deg/day (sidereal). Carrington longitude is defined by this rate.
R_SUN_KM = 695_700              # IAU nominal solar radius
YEAR_DAYS = 365.25


def julian_day(t):
    """UTC timestamps (anything numpy can turn into datetime64) -> Julian Day."""
    ns = np.asarray(t, dtype="datetime64[ns]").astype("int64")
    return ns / 86400e9 + 2440587.5


def sun_longitude(jd):
    """Apparent geocentric ecliptic longitude of the Sun (deg) and obliquity (rad). Meeus ch. 25."""
    T = (np.asarray(jd, float) - 2451545.0) / 36525
    L = 280.46646 + 36000.76983 * T + 0.0003032 * T**2                  # mean longitude
    M = np.radians(357.52911 + 35999.05029 * T - 0.0001537 * T**2)       # mean anomaly
    C = ((1.914602 - 0.004817 * T - 0.000014 * T**2) * np.sin(M)         # equation of centre
         + (0.019993 - 0.000101 * T) * np.sin(2 * M) + 0.000289 * np.sin(3 * M))
    om = np.radians(125.04 - 1934.136 * T)
    lam = L + C - 0.00569 - 0.00478 * np.sin(om)                          # aberration + nutation
    eps = np.radians(23.439291 - 0.0130042 * T + 0.00256 * np.cos(om))
    return lam % 360, eps


def sun_ephemeris(jd):
    """Return B0, L0, P in degrees for Julian Day(s) jd. Meeus ch. 29."""
    jd = np.asarray(jd, float)
    lam_deg, eps = sun_longitude(jd)
    lam = np.radians(lam_deg)
    I = np.radians(7.25)                                                   # solar equator vs ecliptic
    K = np.radians(73.6667 + 1.3958333 * (jd - 2396758) / 36525)           # node of solar equator
    theta = (jd - 2398220) * 360 / 25.38                                   # Carrington meridian angle
    B0 = np.degrees(np.arcsin(np.sin(lam - K) * np.sin(I)))
    eta = np.degrees(np.arctan2(-np.sin(lam - K) * np.cos(I), -np.cos(lam - K)))
    L0 = (eta - theta) % 360
    P = np.degrees(np.arctan(-np.cos(lam) * np.tan(eps)) + np.arctan(-np.cos(lam - K) * np.tan(I)))
    return B0, L0, P


def earth_orbital_rate(jd):
    """How fast the Earth goes round the Sun (deg/day): 0.953 in July ... 1.019 in January."""
    a, _ = sun_longitude(np.asarray(jd, float) - 0.5)
    b, _ = sun_longitude(np.asarray(jd, float) + 0.5)
    return (b - a + 180) % 360 - 180


def pixel_to_helio(x, y, xc, yc, r, B0=0.0, P=0.0):
    """Image pixel -> (latitude, central-meridian distance), both in degrees.

    x, y   : pixel position of the sunspot (y counts DOWN from the top, as in every image program)
    xc, yc : pixel position of the disk centre;  r : disk radius in pixels
    B0     : tilt of the solar north pole toward us (deg);  P : 0 for images with solar north up (SDO)
    West (the direction the Sun rotates toward) is to the right, north is up.
    """
    X = (np.asarray(x, float) - xc) / r            # -1 .. 1, west positive
    Y = -(np.asarray(y, float) - yc) / r           # -1 .. 1, north positive
    p = np.radians(P)
    X, Y = X * np.cos(p) + Y * np.sin(p), -X * np.sin(p) + Y * np.cos(p)
    Z = np.sqrt(np.clip(1 - X**2 - Y**2, 0, None))  # distance toward the observer (sphere: X²+Y²+Z²=1)
    b = np.radians(B0)
    lat = np.degrees(np.arcsin(Y * np.cos(b) + Z * np.sin(b)))
    cmd = np.degrees(np.arctan2(X, Z * np.cos(b) - Y * np.sin(b)))
    return lat, cmd


def helio_to_pixel(lat, cmd, xc, yc, r, B0=0.0):
    """Inverse of pixel_to_helio (P = 0). Used for drawing and for the round-trip test."""
    f, l, b = np.radians(lat), np.radians(cmd), np.radians(B0)
    X = np.cos(f) * np.sin(l)
    Y = np.sin(f) * np.cos(b) - np.cos(f) * np.cos(l) * np.sin(b)
    return xc + X * r, yc - Y * r


def simple_pixel_to_helio(x, y, xc, yc, r):
    """The school-level version (ignores B0): sin(lat) = Y, sin(CMD) = X / cos(lat)."""
    X = (np.asarray(x, float) - xc) / r
    Y = -(np.asarray(y, float) - yc) / r
    lat = np.arcsin(Y)
    return np.degrees(lat), np.degrees(np.arcsin(np.clip(X / np.cos(lat), -1, 1)))


def fit_line(t, v):
    """Least-squares straight line v = a + s*t. Returns slope, its standard error, and rms scatter."""
    t = np.asarray(t, float); v = np.asarray(v, float)
    A = np.vstack([np.ones_like(t), t - t.mean()]).T
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    res = v - A @ coef
    dof = max(len(t) - 2, 1)
    s_err = np.sqrt((res @ res) / dof / ((t - t.mean()) ** 2).sum())
    return coef[1], s_err, np.sqrt((res**2).mean())


def speed_km_s(omega_deg_day, lat_deg):
    """Linear speed of the surface: v = omega * R * cos(latitude)."""
    return np.radians(omega_deg_day) / 86400 * R_SUN_KM * np.cos(np.radians(lat_deg))


if __name__ == "__main__":
    # Self-test 1: our Meeus formulas against SunPy (professional library)
    import pandas as pd
    import astropy.units as u
    from sunpy.coordinates import sun
    print("Ephemeris check (ours vs SunPy):")
    worst = np.zeros(3)
    for d in pd.date_range("2010-01-01", "2026-12-31", periods=40):
        B0, L0, P = sun_ephemeris(julian_day(d.to_datetime64()))
        sB0, sL0, sP = sun.B0(d).deg, sun.L0(d).deg, sun.P(d).deg
        worst = np.maximum(worst, np.abs([B0 - sB0, (L0 - sL0 + 180) % 360 - 180, P - sP]))
    print(f"   largest difference over 40 dates 2010-2026: B0 {worst[0]:.3f}°, L0 {worst[1]:.3f}°, P {worst[2]:.3f}°")
    # Self-test 2: pixel -> heliographic -> pixel round trip
    lat, cmd = np.array([-30, -10, 0, 15, 35]), np.array([-60, -20, 0, 30, 55])
    for B0 in [-7.25, 0, 7.25]:
        x, y = helio_to_pixel(lat, cmd, 1024, 1024, 960, B0)
        la, cm = pixel_to_helio(x, y, 1024, 1024, 960, B0)
        print(f"   round trip B0={B0:+.2f}: max error {max(abs(la - lat).max(), abs(cm - cmd).max()):.1e}°")
    jd = julian_day(np.array(["2026-01-03", "2026-07-04"], dtype="datetime64[ns]"))
    print("   Earth's orbital rate in Jan / Jul:", earth_orbital_rate(jd).round(3), "deg/day")
