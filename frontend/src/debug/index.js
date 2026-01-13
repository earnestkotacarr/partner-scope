/**
 * Debug Module Exports
 *
 * Central export point for all debug-related functionality.
 */

export {
  isDebugMode,
  enableDebugMode,
  disableDebugMode,
  toggleDebugMode,
  debugSettings,
  setDebugSetting,
  debugPages,
} from './config';

export {
  FakeDataGenerator,
  getGenerator,
  generateFakeData,
} from './fakeData';
