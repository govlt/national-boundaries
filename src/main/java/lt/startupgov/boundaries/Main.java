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
            String pmTilesName,
            Layer layer
    ) {
    }

    static final LayerConfiguration[] layerConfigurations = {
            new LayerConfiguration(
                    "Counties of Lithuania",
                    "counties.pmtiles",
                    new Counties()
            ),
            new LayerConfiguration(
                    "Municipalities of Lithuania",
                    "municipalities.pmtiles",
                    new Municipalities()
            ),
            new LayerConfiguration(
                    "Elderships of Lithuania",
                    "elderships.pmtiles",
                    new Elderships()
            ),
            new LayerConfiguration(
                    "Residential areas of Lithuania",
                    "residential-areas.pmtiles",
                    new ResidentialAreas()
            ),
            new LayerConfiguration(
                    "Streets of Lithuania",
                    "streets.pmtiles",
                    new Streets()
            ),
            new LayerConfiguration(
                    "Parcels of Lithuania",
                    "parcels.pmtiles",
                    new Parcels()
            ),
    };

    public static void main(String[] args) {
        for (LayerConfiguration layerConfiguration : layerConfigurations) {
            Planetiler.create(Arguments.fromConfigFile(Path.of("config.properties")))
                    .addGeoPackageSource(
                            Source.BOUNDARIES,
                            Path.of("data", "boundaries-4326.gpkg"),
                            "https://github.com/govlt/national-boundaries/releases/latest/download/boundaries-4326.gpkg"
                    )
                    .overwriteOutput(Path.of("data", "output", layerConfiguration.pmTilesName))
                    .setProfile((runner) -> new Main(layerConfiguration))
                    .run();
        }
    }

    private final LayerConfiguration configuration;

    private Main(LayerConfiguration configuration) {
        this.configuration = configuration;

        registerSourceHandler(Source.BOUNDARIES, configuration.layer);
        registerHandler(configuration.layer);
    }

    @Override
    public String name() {
        return configuration.name();
    }
}


