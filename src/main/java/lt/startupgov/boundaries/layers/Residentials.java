package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Residentials implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.RESIDENTIALS) && sf.canBePolygon()) {
            var fid = sf.getLong("ID");

            features.polygon(Source.RESIDENTIALS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(10)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("GYV_PAV"))
                    .setAttr("code", sf.getTag("GYV_KODAS"))
                    .setAttr("area", sf.getTag("PLOTAS"))
                    .setAttr("municipality_code", sf.getTag("SAV_KODAS"));
        }
    }
}
