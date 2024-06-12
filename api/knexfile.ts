import {typeOf} from "uri-js/dist/esnext/util";

const {knexSnakeCaseMappers} = require('objection');
require('dotenv').config();

export const boundariesConfig = {
    client: 'better-sqlite3',
    connection: {
        filename: './boundaries.sqlite',
    },
    useNullAsDefault: true,
    pool: {min: 0, max: 7},
    ...knexSnakeCaseMappers(),
};
