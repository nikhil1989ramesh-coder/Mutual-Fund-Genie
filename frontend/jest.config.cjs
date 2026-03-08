module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/src/**/*.test.js'],
  transform: {
    '^.+\\.[jt]sx?$': [
      'babel-jest',
      {
        presets: [
          '@babel/preset-env',
          ['@babel/preset-react', { runtime: 'automatic' }],
        ],
      },
    ],
  },
};

