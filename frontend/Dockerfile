# =============================================================================
# Frontend Dockerfile - Next.js Application
# =============================================================================
#
# LEARNING NOTES:
# - Multi-stage builds: deps → builder → runner (smaller final image)
# - Next.js standalone output mode creates minimal production bundle
# - Alpine Linux is tiny (~5MB) but can have compatibility issues
# - Node slim is a good balance between size and compatibility
#
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install node_modules
# -----------------------------------------------------------------------------
FROM node:22-slim AS deps

WORKDIR /app

# Copy package files for dependency installation
# package-lock.json ensures exact versions (if exists)
COPY package.json package-lock.json* ./

# Install dependencies
# --frozen-lockfile: Fail if lockfile needs update (CI safety)
# ci would be better but we'll use install for flexibility
RUN npm ci --ignore-scripts

# -----------------------------------------------------------------------------
# Stage 2: Builder - Build the Next.js application
# -----------------------------------------------------------------------------
FROM node:22-slim AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build arguments for environment variables needed at build time
# These can be overridden with: docker build --build-arg API_URL=xxx
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Set environment variables for the build
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application
# This creates optimized production bundles
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Runner - Minimal production image
# -----------------------------------------------------------------------------
FROM node:22-slim AS runner

WORKDIR /app

# Set to production mode
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Security: Create non-root user
RUN groupadd --gid 1001 nodejs && \
    useradd --uid 1001 --gid nodejs nextjs

# Copy only what's needed to run the application
# public folder: static assets (images, fonts, etc.)
COPY --from=builder /app/public ./public

# Copy the standalone build output
# Next.js standalone mode creates a minimal server
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Document the port
EXPOSE 3000

# Switch to non-root user
USER nextjs

# Health check for the frontend
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1

# Start the Next.js server
# server.js is created by standalone output mode
CMD ["node", "server.js"]
