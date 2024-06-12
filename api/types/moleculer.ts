import moleculer, { Context } from 'moleculer';
import { ActionSchema, ActionParamSchema } from 'moleculer';
import { IncomingMessage } from 'http';

export type FieldHookCallback = {
  ctx: Context;
  value: any;
  params: any;
  field: any;
  operation: any;
  entity: any;
};

export interface EntityChangedParams<T> {
  type: 'create' | 'update' | 'replace' | 'remove' | 'clear';
  data: T;
  oldData?: T;
}
export type MultipartMeta = {
  $multipart: Record<string, string>;
  $params: Record<string, string>;
  fieldname: string;
  filename: string;
  encoding: string;
  mimetype: string;
};

export type ContextMeta<T> = { ctx: { meta: T } };

export interface DBPagination<T> {
  rows: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface RouteSchemaOpts {
  path: string;
  whitelist?: string[];
  authorization?: boolean;
  authentication?: boolean;
  aliases?: any;
}

export interface RouteSchema {
  path: string;
  mappingPolicy?: 'restricted' | 'all';
  opts: RouteSchemaOpts;
  middlewares: ((req: any, res: any, next: any) => void)[];
  authorization?: boolean;
  authentication?: boolean;
  logging?: boolean;
  etag?: boolean;
  cors?: any;
  rateLimit?: any;
  whitelist?: string[];
  hasWhitelist: boolean;
  callOptions?: any;
}

export interface RequestMessage extends IncomingMessage {
  $action: ActionSchema;
  $params: ActionParamSchema;
  $route: RouteSchema;
}
