// Thursday's World — news-image-20261126.
//
// This program only validates the pre-drawn entry.png that ships in
// this repository and copies it to the output directory. It draws
// nothing, runs nothing else, and needs no network and no library
// beyond the Node standard library.
//
// Validation: PNG signature, a full chunk walk with hand-rolled
// CRC-32 over every chunk, IHDR 1024x1024, at least one IDAT chunk,
// IEND as the final chunk at end of file, and the 1 MiB size cap.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1048576;
const WANT_WIDTH = 1024;
const WANT_HEIGHT = 1024;

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function die(message: string): never {
  console.error("entry check failed: " + message);
  process.exit(1);
}

// CRC-32 (IEEE 802.3, polynomial 0xedb88320), built at startup.
const CRC_TABLE: Uint32Array = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(bytes: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) {
    c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function u32be(bytes: Buffer, offset: number): number {
  return bytes.readUInt32BE(offset);
}

function checkPng(bytes: Buffer): void {
  if (bytes.length < 8 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    die("not a PNG file");
  }
  if (bytes.length > MAX_BYTES) {
    die("file is " + bytes.length + " bytes, over the 1048576 cap");
  }
  let pos = 8;
  let sawIhdr = false;
  let sawIdat = false;
  let sawIend = false;
  while (pos + 8 <= bytes.length) {
    const length = u32be(bytes, pos);
    const type = bytes.subarray(pos + 4, pos + 8).toString("latin1");
    const dataStart = pos + 8;
    const dataEnd = dataStart + length;
    const crcEnd = dataEnd + 4;
    if (crcEnd > bytes.length) {
      die("chunk " + type + " runs past end of file");
    }
    const stored = u32be(bytes, dataEnd);
    const actual = crc32(bytes.subarray(pos + 4, dataEnd));
    if (stored !== actual) {
      die("chunk " + type + " has a bad CRC");
    }
    if (type === "IHDR") {
      if (sawIhdr) die("two IHDR chunks");
      if (length !== 13) die("IHDR is not 13 bytes");
      sawIhdr = true;
      const width = u32be(bytes, dataStart);
      const height = u32be(bytes, dataStart + 4);
      if (width !== WANT_WIDTH || height !== WANT_HEIGHT) {
        die("image is " + width + "x" + height + ", want 1024x1024");
      }
      const bitDepth = bytes[dataStart + 8];
      const colorType = bytes[dataStart + 9];
      if (bitDepth !== 8) die("bit depth is " + bitDepth + ", want 8");
      if (colorType !== 2 && colorType !== 6) {
        die("color type is " + colorType + ", want 2 or 6");
      }
    } else if (type === "IDAT") {
      if (!sawIhdr) die("IDAT before IHDR");
      sawIdat = true;
    } else if (type === "IEND") {
      if (!sawIhdr || !sawIdat) die("IEND without IHDR/IDAT");
      if (length !== 0) die("IEND carries data");
      sawIend = true;
      if (crcEnd !== bytes.length) die("bytes after IEND");
      break;
    }
    pos = crcEnd;
  }
  if (!sawIhdr) die("no IHDR chunk");
  if (!sawIdat) die("no IDAT chunk");
  if (!sawIend) die("no IEND chunk at end of file");
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  if (!existsSync(source)) die("entry.png is missing from the repository");
  const bytes = readFileSync(source);
  checkPng(bytes);

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  writeFileSync(target, bytes);
  console.log(
    "ok: entry.png " + bytes.length + " bytes, 1024x1024, copied to " + target,
  );
}

main();
