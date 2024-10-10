package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.geo.GeometryException;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;
import org.geotools.process.geometry.GeometryFunctions;

public class Municipalities implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.MUNICIPALITIES) && sf.canBePolygon()) {
            var featureId = sf.getLong("feature_id");

            features.polygon(Layers.MUNICIPALITIES)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(featureId)
                    .setAttr("feature_id", featureId)
                    .setAttr("code", sf.getTag("code"))
                    .setAttr("county_code", sf.getTag("county_code"))
                    .setAttr("name", sf.getTag("name"));

            try {
                var pointGeom = GeometryFunctions.interiorPoint(sf.polygon());
    
                features.geometry(Layers.MUNICIPALITIES_LABEL, pointGeom)
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
