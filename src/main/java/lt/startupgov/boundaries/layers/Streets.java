package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Streets implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.RESIDENTIALS) && sf.canBeLine()) {
            var fid = sf.getLong("FID");

            features.line(Source.RESIDENTIALS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("GYV_PAV"))
                    .setAttr("code", sf.getTag("GAT_KODAS"))
                    .setAttr("area", sf.getTag("PLOTAS"))
                    .setAttr("municipality_code", sf.getTag("SAV_KODAS"));
        }
    }
}
