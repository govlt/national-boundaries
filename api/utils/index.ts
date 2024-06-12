import { Readable } from 'stream';

export function toReadableStream(fetchReadable: any): NodeJS.ReadableStream {
  if (!fetchReadable) return;
  return new Readable({
    async read() {
      if (!fetchReadable?.read) {
        this.emit('done');
        return;
      }

      const { value, done } = await fetchReadable.read();
      if (done) {
        this.emit('end');
        return;
      }

      this.push(value);
    },
  });
}
