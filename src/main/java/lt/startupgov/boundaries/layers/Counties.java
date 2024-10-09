package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.geo.GeometryException;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;
import org.geotools.process.geometry.GeometryFunctions;

public class Counties implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.COUNTIES) && sf.canBePolygon()) {
            var featureId = sf.getLong("feature_id");

            features.polygon(Layers.COUNTIES)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(featureId)
                    .setAttr("feature_id", featureId)
                    .setAttr("name", sf.getTag("name"))
                    .setAttr("code", sf.getTag("code"));

            try {
                var pointGeom = GeometryFunctions.interiorPoint(sf.polygon());
    
                features.geometry(Layers.COUNTIES_LABEL, pointGeom)
                        .setBufferPixels(4)
                        .setMinPixelSizeAtAllZooms(0)
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
