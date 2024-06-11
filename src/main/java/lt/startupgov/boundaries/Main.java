package lt.startupgov.boundaries;

import com.onthegomap.planetiler.ForwardingProfile;
import com.onthegomap.planetiler.Planetiler;
import com.onthegomap.planetiler.config.Arguments;
import lt.startupgov.boundaries.constants.Source;
import lt.startupgov.boundaries.layers.Layer;
import lt.startupgov.boundaries.layers.Municipalities;

import java.nio.file.Path;

public class Main extends ForwardingProfile {

    private record LayerConfiguration(
            String name,
            String sourceName,
            String pmTilesName,
            Layer layer
    ) {
    }

    static final LayerConfiguration[] layerConfigurations = {
            new LayerConfiguration(
                    "Municipal Boundaries of Lithuania",
                    Source.MUNICIPALITIES,
                    "municipalities.pmtiles",
                    new Municipalities()
            ),
    };

    public static void main(String[] args) throws Exception {
        for (LayerConfiguration layerConfiguration : layerConfigurations) {
            Planetiler.create(Arguments.fromConfigFile(Path.of("config.properties")))
                    .addGeoPackageSource(
                            Source.MUNICIPALITIES,
                            Path.of("data", "sources", "espg-4326", "municipalities.gpkg.zip"),
                            "https://cdn.biip.lt/tiles/poc/gpkg/municipalities.gpkg.zip"
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


