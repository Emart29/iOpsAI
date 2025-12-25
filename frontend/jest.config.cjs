/** @type {import('jest').Config} */
module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
    transform: {
        '^.+\\.(ts|tsx)$': 'ts-jest',
    },
    testPathIgnorePatterns: ['/node_modules/', '/dist/'],
};
