package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.ForwardingProfile;

public interface Layer extends
        ForwardingProfile.Handler,
        ForwardingProfile.FeatureProcessor {

}