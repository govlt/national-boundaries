package lt.startupgov.boundaries;

import com.onthegomap.planetiler.ForwardingProfile;
import com.onthegomap.planetiler.Planetiler;
import com.onthegomap.planetiler.config.Arguments;
import lt.startupgov.boundaries.constants.Source;
import lt.startupgov.boundaries.layers.*;

import java.nio.file.Path;

public class Main extends ForwardingProfile {

    private record LayerConfiguration(
            String name,
            String sourceName,
            String pmTilesName,
            Layer layer,
            Path path,
            String url
    ) {
    }

    static final LayerConfiguration[] layerConfigurations = {
            new LayerConfiguration(
                    "Counties of Lithuania",
                    Source.COUNTIES,
                    "counties.pmtiles",
                    new Counties(),
                    Path.of("data", "sources", "counties-4326.gpkg.zip"),
                    "https://cdn.biip.lt/tiles/poc/gpkg/counties.gpkg.zip"
            ),
            new LayerConfiguration(
                    "Municipalities of Lithuania",
                    Source.MUNICIPALITIES,
                    "municipalities.pmtiles",
                    new Municipalities(),
                    Path.of("data", "sources", "municipalities-4326.gpkg.zip"),
                    "https://cdn.biip.lt/tiles/poc/gpkg/municipalities.gpkg.zip"
            ),
            new LayerConfiguration(
                    "Elderships of Lithuania",
                    Source.ELDERSHIPS,
                    "elderships.pmtiles",
                    new Elderships(),
                    Path.of("data", "sources", "elderships-4326.gpkg.zip"),
                    "https://cdn.biip.lt/tiles/poc/gpkg/elderships.gpkg.zip"
            ),
            new LayerConfiguration(
                    "Residential areas of Lithuania",
                    Source.RESIDENTIALS,
                    "residentials.pmtiles",
                    new Residentials(),
                    Path.of("data", "sources", "residentials-4326.gpkg.zip"),
                    "https://cdn.biip.lt/tiles/poc/gpkg/residentials.gpkg.zip"
            ),
            new LayerConfiguration(
                    "Streets of Lithuania",
                    Source.STREETS,
                    "streets.pmtiles",
                    new Streets(),
                    Path.of("data", "sources", "streets-4326.gpkg.zip"),
                    "https://cdn.biip.lt/tiles/poc/gpkg/streets.gpkg.zip"
            ),
    };

    public static void main(String[] args) throws Exception {
        for (LayerConfiguration layerConfiguration : layerConfigurations) {
            Planetiler.create(Arguments.fromConfigFile(Path.of("config.properties")))
                    .addGeoPackageSource(
                            layerConfiguration.sourceName,
                            layerConfiguration.path,
                            layerConfiguration.url
                    )
                    .overwriteOutput(Path.of("data", "output", layerConfiguration.pmTilesName))
                    .setProfile((runner) -> new Main(layerConfiguration))
                    .run();
        }
    }

    private final LayerConfiguration configuration;

    private Main(LayerConfiguration configuration) {
        this.configuration = configuration;

        registerSourceHandler(configuration.sourceName, configuration.layer);
        registerHandler(configuration.layer);
    }

    @Override
    public String name() {
        return configuration.name();
    }
}


