<?php
declare(strict_types=1);

/**
 * Strict semantic-quality gate.
 *
 * These routes stay navigable while their calculation model is being upgraded,
 * but are excluded from the verified-live/indexable contract. A route may leave
 * this list only after its rule semantics are benchmarked by date/time fixtures,
 * not merely by result shape/count.
 */
return [
    'panchang/kranti-samya' => 'Mahapata interval requires exact Kranti-Samya methodology; current engine is only a declination-convergence approximation.',
    'muhurat/pancha-pakshi' => 'Personalized Pancha Pakshi requires verified Paksha/weekday mirror tables, birth-bird selection and unequal sub-period rules.',
    'vrat/chandra-darshan' => 'Moonset-after-sunset is not a sufficient crescent-visibility model.',
    'vrat/ishti-anvadhan' => 'Current midpoint pairing needs exact observance-date fixtures.',
    'vrat/shraddha' => 'Full Shraddha calendar must cover the complete traditional observance classes, not only a subset.',
    'jyotish/pancha-pakshi' => 'Birth-bird mapping must be lineage/profile explicit rather than Nakshatra-index modulo five.',
    'jyotish/gemstone' => 'Lagna-lord-only mapping is a reference shortcut, not a complete gemstone suitability calculation.',
    'jyotish/rudraksha' => 'Lagna-lord-only mapping is a reference shortcut, not a complete Rudraksha suitability calculation.',
    'jyotish/sahasra-chandrodaya' => 'Mean synodic-month multiplication is an estimate, not exact 1000-moonrise/phase enumeration.',
    'jyotish/prashnavali' => 'Nakshatra modulo scoring is not a recognized Prashnavali method.',
    'jyotish/rashi-by-name' => 'Name-initial mapping is tradition-dependent and currently too coarse for calculator certification.',
];
