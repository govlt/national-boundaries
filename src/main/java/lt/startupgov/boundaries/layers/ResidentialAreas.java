package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.geo.GeometryException;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;
import org.geotools.process.geometry.GeometryFunctions;

public class ResidentialAreas implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.RESIDENTIAL_AREAS) && sf.canBePolygon()) {
            var featureId = sf.getLong("feature_id");

            features.polygon(Layers.RESIDENTIAL_AREAS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(10)
                    .setId(featureId)
                    .setAttr("feature_id", featureId)
                    .setAttr("name", sf.getTag("name"))
                    .setAttr("code", sf.getTag("code"))
                    .setAttr("municipality_code", sf.getTag("municipality_code"));

            try {
                var pointGeom = GeometryFunctions.interiorPoint(sf.polygon());
    
                features.geometry(Layers.RESIDENTIAL_AREAS_LABEL, pointGeom)
                        .setBufferPixels(4)
                        .setMinPixelSizeAtAllZooms(0)
                        .setMinZoom(10)
                        .setId(featureId)
                        .setAttr("feature_id", featureId)
                        .setAttr("code", sf.getTag("code"))
                        .setAttr("name", sf.getTag("name"));
            } catch (GeometryException e) {
                throw new RuntimeException(e);
            }
        }
    }
}
