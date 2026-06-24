-- Demo geolocation + liveness for the documentation screenshots.
--
-- There is no REST/agent path to set map coordinates directly (the server only
-- derives them from GeoIP on a reported public IP), and GeoIP is disabled on the
-- screenshot VM for privacy. So we write FAKE, plausible data-center coordinates
-- straight into the host rows — the /map view shows worldwide markers and NEVER
-- the operator's real location.
--
-- We also bump last_access to now so each host renders as "up" (the UI marks a
-- host up when last_access is within the last 5 minutes).
--
-- "host" is a reserved word, hence the quoting. Applied via:
--   vagrant ssh -c "sudo -u postgres psql -d sysmanage -f /vagrant/seed_geo.sql"

UPDATE "host" SET geo_latitude=37.3382,  geo_longitude=-121.8863, geo_city='San Jose',  geo_country_code='US', public_ip='151.101.1.140', public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='ubuntu-web-01.corp.northstar.io';
UPDATE "host" SET geo_latitude=39.0438,  geo_longitude=-77.4874,  geo_city='Ashburn',   geo_country_code='US', public_ip='104.16.132.229', public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='rhel-db-01.corp.northstar.io';
UPDATE "host" SET geo_latitude=50.1109,  geo_longitude=8.6821,    geo_city='Frankfurt', geo_country_code='DE', public_ip='140.82.112.3',   public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='debian-app-01.corp.northstar.io';
UPDATE "host" SET geo_latitude=51.5074,  geo_longitude=-0.1278,   geo_city='London',    geo_country_code='GB', public_ip='185.199.108.153', public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='freebsd-build-01.corp.northstar.io';
UPDATE "host" SET geo_latitude=-33.8688, geo_longitude=151.2093,  geo_city='Sydney',    geo_country_code='AU', public_ip='20.190.160.2',   public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='win11-ws-01.corp.northstar.io';
UPDATE "host" SET geo_latitude=35.6762,  geo_longitude=139.6503,  geo_city='Tokyo',     geo_country_code='JP', public_ip='17.253.144.10',  public_ip_resolved_at=NOW(), last_access=NOW() WHERE fqdn='macos-studio-01.corp.northstar.io';

-- PRIVACY belt-and-suspenders: scrub geolocation from any NON-demo host (e.g. the
-- VM's own real agent, which may have geolocated the operator's real WAN IP during
-- an earlier run when GeoIP was still enabled). Only the six fake demo markers above
-- ever appear on the map.
UPDATE "host" SET geo_latitude=NULL, geo_longitude=NULL, geo_city=NULL, geo_country_code=NULL, public_ip=NULL
WHERE fqdn NOT LIKE '%.corp.northstar.io';
