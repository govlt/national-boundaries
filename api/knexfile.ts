import {typeOf} from "uri-js/dist/esnext/util";

const {knexSnakeCaseMappers} = require('objection');
require('dotenv').config();

export const boundariesConfig = {
    client: 'better-sqlite3',
    connection: {
        filename: './boundaries.sqlite',
    },
    useNullAsDefault: true,
    pool: {
        min: 1,
        max: 7,
        afterCreate: (conn: any, done: any) => {
            conn.loadExtension(`mod_spatialite`);

            done(null, conn);
        },
    },
    ...knexSnakeCaseMappers(),
};
