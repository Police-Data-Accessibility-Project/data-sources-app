import { expect } from 'vitest';
import vueSnapshotSerializer from './serializer';

expect.addSnapshotSerializer(vueSnapshotSerializer);
