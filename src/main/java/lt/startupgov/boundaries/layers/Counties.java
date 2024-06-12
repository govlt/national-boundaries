package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Counties implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.COUNTIES) && sf.canBePolygon()) {
            // For some re
            var fid = sf.getLong("fid");

            features.polygon(Source.COUNTIES)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("APS_PAV"))
                    .setAttr("code", sf.getTag("APS_KODAS"))
                    .setAttr("area", sf.getTag("APS_PLOTAS"));
        }
    }
}
