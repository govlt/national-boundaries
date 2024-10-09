# National Boundaries Vector Tiles of Lithuania

Access simplified and regularly updated vector tiles of national boundaries in Lithuania from the Address Registry.

## Key Features

1. **Ready to Use**: Pre-simplified and ready-to-serve vector tiles.
2. **Easy Hosting**: Available as a single-file PMTiles archive, easily hosted on platforms like S3.
3. **Regular Updates**: Daily updates reflecting boundary changes.
4. **Available Hosted Versions**: Hosted versions of boundaries are readily available for direct use.
5. **Open Source**: Free and open-source. Join our community of contributors.

## Usage

For details on using PMTiles, check the [PMTiles in the browser](https://docs.protomaps.com/pmtiles/maplibre)
documentation.

### Hosted Versions

Use hosted versions of boundaries on your website, with global low latency and high SLA via Cloudflare Pages.

| Type                  | Lithuanian Translation    | Demo                                                                                                                            | PMTiles Archive URL                                                                       |
| --------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **Counties**          | Apskričių ribos           | [Demo](https://pmtiles.io/?url=https%3A%2F%2Fboundaries.startupgov.lt%2Fpmtiles%2Fcounties.pmtiles#map=6.95/55.191/22.92)       | [counties.pmtiles](https://boundaries.startupgov.lt/pmtiles/counties.pmtiles)             |
| **Municipalities**    | Savivaldybių ribos        | [Demo](https://pmtiles.io/?url=https%3A%2F%2Fboundaries.startupgov.lt%2Fpmtiles%2Fmunicipalities.pmtiles#map=6.95/55.191/22.92) | [municipalities.pmtiles](https://boundaries.startupgov.lt/pmtiles/municipalities.pmtiles) |
| **Elderships**        | Seniūnijų ribos           | [Demo](https://pmtiles.io/?url=https%3A%2F%2Fboundaries.startupgov.lt%2Fpmtiles%2Felderships.pmtiles#map=6.95/55.191/22.92)     | [elderships.pmtiles](https://boundaries.startupgov.lt/pmtiles/elderships.pmtiles)         |
| **Residential Areas** | Gyvenamųjų vietovių ribos | -                                                                                                                               | Not Available                                                                             |
| **Streets**           | Gatvių ribos              | [Demo](https://pmtiles.io/?url=https%3A%2F%2Fboundaries.startupgov.lt%2Fpmtiles%2Fstreets.pmtiles#map=11/54.6828/25.2686)       | [streets.pmtiles](https://boundaries.startupgov.lt/pmtiles/streets.pmtiles)               |
| **Parcels**           | Žemės sklypų ribos        | -                                                                                                                               | Not Available                                                                             |

### Self-Hosting

#### PMTiles

Download the latest PMTiles archives and host them on your own server.

| Type                  | Lithuanian Translation    | PMTiles Archive URL                                                                                                                                      |
| --------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Counties**          | Apskričių ribos           | [counties.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/counties.pmtiles)                                               |
| **Municipalities**    | Savivaldybių ribos        | [municipalities.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/municipalities.pmtiles)                                   |
| **Elderships**        | Seniūnijų ribos           | [elderships.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/elderships.pmtiles)                                           |
| **Residential Areas** | Gyvenamųjų vietovių ribos | [residential-areas.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/residential-areas.pmtiles)                             |
| **Streets**           | Gatvių ribos              | [streets.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/streets.pmtiles)                                                 |
| **Parcels**           | Žemės sklypų ribos        | [parcels.pmtiles](https://github.com/govlt/national-boundaries/releases/latest/download/parcels.pmtiles)<br/>(**Important:** visible from zoom level 14) |

Ensure to periodically download the PMTiles archives mentioned above to
your own S3 or file storage and utilize them as needed.

#### Docker Vector Tiles

Utilize the provided Docker
image [national-boundaries-vector](https://github.com/govlt/national-boundaries/pkgs/container/national-boundaries-vector),
which includes all PMTiles enabling you to serve vector tiles on-the-fly.

Here's an example of its usage with Docker Compose:

```yaml
services:
  national-boundaries-vector:
    image: ghcr.io/govlt/national-boundaries-vector:stable
    pull_policy: always
    restart: unless-stopped
    ports:
      - "80:80"
    healthcheck:
      test: [ "CMD-SHELL", "wget --no-verbose --tries=1 --spider http://127.0.0.1:80/health || exit 1" ]
      interval: 5s
      timeout: 3s
      start_period: 5s
      retries: 5
```

## Architecture

```mermaid
flowchart TD
    rc["<a href='https://www.registrucentras.lt'>State Enterprise Centre of Registers</a>"]
    rc-->ar["<a href='https://www.registrucentras.lt/p/1187'>Address Registry raw data</a>"]
    rc-->pr["<a href='https://www.registrucentras.lt/p/1092'>Parcels raw data</a>"]

    transform["<a href='https://github.com/govlt/national-boundaries/blob/main/create-geopackage.sh'>Create GeoPackage</a>"]-->|"<a href='https://github.com/govlt/national-boundaries/releases/latest/download/boundaries-4326.gpkg'>boundaries-4326.gpkg</a>"|github-releases    
    
    github-releases["<a href='https://github.com/govlt/national-boundaries/releases'>GitHub Releases</a>"]--> cloudflare-pages["Cloudflare Pages"]

    ar-->transform
    pr-->transform
    
    cloudflare-pages-->pages-counties["<a href='https://boundaries.startupgov.lt/pmtiles/counties.pmtiles'>counties.pmtiles</a>"]
    cloudflare-pages-->pages-municipalities["<a href='https://boundaries.startupgov.lt/pmtiles/municipalities.pmtiles'>municipalities.pmtiles</a>"]
    cloudflare-pages-->pages-elderships["<a href='https://boundaries.startupgov.lt/pmtiles/elderships.pmtiles'>elderships.pmtiles</a>"]
    cloudflare-pages-->pages-streets["<a href='https://boundaries.startupgov.lt/pmtiles/streets.pmtiles'>streets.pmtiles</a>"]
```

## Development Setup

- **Install Java 21+**: Ensure Java is installed for running the mapping engine.

### Generating Tiles

To generate the tiles in PMTiles format:

```shell
make generate
```

Find the output in `data/output`.

### Previewing

Ensure [Docker](https://www.docker.com/get-started/) (version 2.22+ preferred) is installed. Then, run:

```shell
make preview
```

This will start [Tileserver-GL](https://github.com/maptiler/tileserver-gl) at http://localhost:8080 for previewing.

## License

This project is licensed under the [MIT License](./LICENSE). Data is licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.lt). For more information,
visit [Registrų centras](https://www.registrucentras.lt/p/1187).

While preparing the National Boundaries Vector Tiles, some changes were made, such as changing attribute names to
English. For full details, check out the [create-geopackage.sh](./create-geopackage.sh) file.

## Contributing

We welcome contributions! For details, see
our [contribution guidelines](https://github.com/govlt/.github/blob/main/CONTRIBUTING.md).
