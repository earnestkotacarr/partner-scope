/**
 * Model Preset Configurations
 *
 * Defines preset options for AI model selection across pipeline stages.
 * Users can choose between Quality, Balanced, and Fast modes.
 */

export const MODEL_PRESETS = {
  quality: {
    id: 'quality',
    name: 'Quality',
    description: 'Best results (~$0.32/search, 20-30 min)',
    models: {
      search: 'gpt-5',
      chat: 'gpt-5',
      refinement: 'gpt-5',
      evaluation: 'gpt-5',
    },
    costLevel: 3,
    speedLevel: 1,
  },
  balanced: {
    id: 'balanced',
    name: 'Balanced',
    description: 'Good quality (~$0.18/search, ~20s)',
    models: {
      search: 'gpt-4.1',
      chat: 'gpt-4o-mini',
      refinement: 'gpt-4o-mini',
      evaluation: 'gpt-4.1',
    },
    costLevel: 2,
    speedLevel: 2,
  },
  fast: {
    id: 'fast',
    name: 'Fast',
    description: 'Fastest (~$0.05/search, ~5s)',
    models: {
      search: 'gpt-4o-mini',
      chat: 'gpt-4o-mini',
      refinement: 'gpt-4o-mini',
      evaluation: 'gpt-4o-mini',
    },
    costLevel: 1,
    speedLevel: 3,
  },
};

export const DEFAULT_PRESET = 'balanced';

/**
 * Get the model configuration for a given preset
 * @param {string} presetId - The preset ID ('quality', 'balanced', or 'fast')
 * @returns {object} The models configuration object
 */
export const getModelConfigForPreset = (presetId) => {
  return MODEL_PRESETS[presetId]?.models || MODEL_PRESETS.balanced.models;
};
