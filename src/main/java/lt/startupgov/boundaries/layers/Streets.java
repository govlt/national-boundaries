package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;

public class Streets implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.STREETS)) {
            var fid = sf.getLong("feature_id");

            features.line(Layers.STREETS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(10)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("name"))
                    .setAttr("full_name", sf.getTag("full_name"))
                    .setAttr("code", sf.getTag("code"))
                    .setAttr("residential_area_code", sf.getTag("residential_area_code"));
        }
    }

}
