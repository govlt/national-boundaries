import {beforeAll, afterAll, describe, it, expect} from 'vitest';
// @ts-ignore
import LocalWebServer from "local-web-server";
import {MunicipaliesReader} from "./municipality";
import {bbox, bboxPolygon, polygon} from "@turf/turf";

async function genToArray<T>(gen: AsyncIterable<T>): Promise<T[]> {
    const arr: T[] = []
    for await(const x of gen) {
        arr.push(x);
    }
    return arr;
}

describe('municipality', () => {
    let lws: LocalWebServer;
    beforeAll(async () => {
        lws = await LocalWebServer.create();
    });
    afterAll(() => {
        if (lws) lws.server.close();
    });

    it('can count municipalities', async () => {
        const testUrl = `http://localhost:${lws.config.port}/test/data/municipalities.fgb`;

        const municipalityReader = await MunicipaliesReader.open(testUrl);

        expect(60).toBe(municipalityReader.count());
    });

    it('can read single municipality by bounding box', async () => {
        const testUrl = `http://localhost:${lws.config.port}/test/data/municipalities.fgb`;

        const municipalityReader = await MunicipaliesReader.open(testUrl);

        const varenaCenterPolygon = polygon(
            [
                [
                    [
                        24.565433052071143,
                        54.215849272239836
                    ],
                    [
                        24.565433052071143,
                        54.20571892536029
                    ],
                    [
                        24.583090071675088,
                        54.20571892536029
                    ],
                    [
                        24.583090071675088,
                        54.215849272239836
                    ],
                    [
                        24.565433052071143,
                        54.215849272239836
                    ]
                ]
            ]
        );
        polygon([
            [
                [
                    25.287164917098778,
                    54.68985604215064
                ],
                [
                    25.287164917098778,
                    54.68195119163565
                ],
                [
                    25.29894784130272,
                    54.68195119163565
                ],
                [
                    25.29894784130272,
                    54.68985604215064
                ],
                [
                    25.287164917098778,
                    54.68985604215064
                ]
            ]
        ]);
        const municipalities = await genToArray(municipalityReader.list(varenaCenterPolygon));
        const municipality = municipalities[0];

        expect(1).toBe(municipalities.length);
        expect(municipality).toBeDefined;

        // @ts-ignore
        const properties = municipality.getProperties();
        expect(properties).toBeDefined;

        expect("Varėnos r. sav.").toBe(properties['SAV_PAV']);
        expect("38").toBe(properties['SAV_KODAS']);
    });

    it('can read single municipality by bounding box which covers multiple municipalities', async () => {
        const testUrl = `http://localhost:${lws.config.port}/test/data/municipalities.fgb`;

        const municipalityReader = await MunicipaliesReader.open(testUrl);

        const vilniusCenterPolygon = polygon([
            [
                [
                    25.287164917098778,
                    54.68985604215064
                ],
                [
                    25.287164917098778,
                    54.68195119163565
                ],
                [
                    25.29894784130272,
                    54.68195119163565
                ],
                [
                    25.29894784130272,
                    54.68985604215064
                ],
                [
                    25.287164917098778,
                    54.68985604215064
                ]
            ]
        ]);


        const municipalities = await genToArray(municipalityReader.list(vilniusCenterPolygon));
        const municipality = municipalities[0];

        expect(1).toBe(municipalities.length);
        expect(municipality).toBeDefined;

        // @ts-ignore
        const properties = municipality.getProperties();
        expect(properties).toBeDefined;

        expect("Vilniaus m. sav.").toBe(properties['SAV_PAV']);
    });

});
