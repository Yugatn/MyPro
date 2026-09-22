# Cinema Catharsis and MyPro

Cinema Catharsis is a connected research and measurement layer for MyPro. It describes what is present in media, how it is distributed in time, how categories co-occur, and how reliable the coding is. It does not turn those measurements into a universal harm score or a claim about what a viewer will feel or do.

MyPro provides content, timeline, fragments, observations, provenance, versions and publication context. Cinema Catharsis provides a formal descriptive ontology and measurement layer over those observations.

## Methodological boundary

The methodology keeps these layers separate:

CONTENT, EXPOSURE, RESPONSE, EFFECT, HARM

CONTENT is directly measurable from media. Exposure can be measured only when an actual viewing context is observed. Response and effect require separate audience evidence. Harm is a further causal and normative question.

Therefore:

- CONTENT is not RESPONSE.
- CONTENT is not HARM.
- screen_time_share is not viewer_exposure.
- coding confidence is not statistical significance.
- an observation is not a conclusion.
- a proposal is not an action.

Cinema Catharsis does not automatically infer viewer harm, audience attitude, causal effect, or a recommendation from media content alone.

## Ontology

The descriptive ontology contains ten broad families:

1. consumption
2. action
3. interaction
4. corporeality
5. environment
6. attributes
7. narrative
8. communication
9. economics
10. social, civic, ideological and identity representation

The tenth family includes friendship, love, trust, respect, care, solidarity, cooperation, civic participation, political or identity representation and social-value programs.

Coding may distinguish these levels: observed, represented, rewarded, advocated, reinforced, effect.

The final level is not inferred by the content coder. It requires independent evidence.

## Core notation

Let T be analyzed duration, omega be one content category, p_i,omega be the coding weight of event i, and [t_i, u_i) be its exact interval.

### Weighted event count

N_omega = sum_i p_i,omega

A binary coding uses p_i,omega = 1. Partial assignment may use a value from 0 to 1. The weight describes coding assignment, not viewer response.

### Category duration

T_omega = mu(union_i [t_i, u_i))

The union prevents overlapping observations in the same category from artificially multiplying screen time.

### Screen-time share

S_omega = T_omega / T

This is a descriptive share of the analyzed timeline.

### Event density

rho_events,omega = N_omega / (T / 60)

The result is weighted events per minute.

### Coverage

C_omega = T_omega,covered / T_omega,target

The implementation bounds the result to the interval from 0 to 1.

### Time density

rho_time,omega = N_omega / T_omega

This describes event concentration relative to occupied category time. It is not a physiological intensity measure.

### Repeatability

R_omega = K_omega / K

K is the number of episodes and K_omega is the number of episodes containing the category.

### Relative category distribution

For a selected category set Omega*:

P_omega^(Omega*) = S_omega / sum_h S_h

This is useful for a Content Wheel or category distribution view. It is not a probability of viewer response.

### Union duration of selected categories

T_Omega* = mu(union over omega in Omega* of union_i [t_i, u_i))

Overlaps between categories are counted once.

### Normalized entropy

For a selected category set with normalized proportions p_omega:

H = -sum p_omega log(p_omega)

H_norm = H / log(k)

This describes temporal distribution across selected categories. It does not measure quality, danger, or psychological effect.

### Coding uncertainty

epsilon_omega = 1 - mean(q_i)

where q_i is coding confidence for events in category omega when confidence is available.

This epsilon describes classification or coding uncertainty. It is not a confidence interval, p-value, effect size, or uncertainty about audience response.

### Category co-occurrence

M_(omega,psi) = T_(omega intersection psi) / T_(omega union psi)

This is a duration-based Jaccard similarity.

## Reliability and accuracy

Cinema Catharsis keeps measurement reliability separate from classifier confidence.

For human or validated coding, inter-coder reliability may be reported with Krippendorff's alpha. Classification quality may separately report:

precision = TP / (TP + FP)

recall = TP / (TP + FN)

confidence is not accuracy.

Project governance may use alpha thresholds such as alpha >= 0.67 for acceptable coding, 0.40 <= alpha < 0.67 for protocol revision, and alpha < 0.40 for rejecting the coding as insufficiently reliable. These are governance thresholds for the coding process, not universal scientific laws.

## Media impact model

Cinema Catharsis also defines a separate systems-level layer:

System = subjects + connections + transmission rules + time

A system effect can depend on scale, exposure saturation, feedback amplification, transmission structure, temporal persistence and cascade conditions.

SystemEffect = f(scale, saturation, amplification, transmission, persistence, cascade)

This is a model boundary, not a formula for predicting the behavior of real people. Empirical audience studies are required before estimating response or effect parameters.

## Integration with MyPro

| Cinema Catharsis | MyPro |
| --- | --- |
| content item | MediaAsset / source content |
| coded event | ContentFragment + Observation |
| time interval | exact TimeRange |
| detector or coder | analyzer identity and version |
| coding confidence | Observation confidence |
| uncertainty | Observation uncertainty |
| category ontology | fragment kind, label and attributes |
| temporal distribution | FragmentIndex / analysis report |
| content version | published version |
| source trace | provenance |
| proposed interpretation | Proposal |
| accepted editorial use | Decision + Revision |

The same source range can therefore be analyzed once and reused by the Viewer-Editor, montage system, social feed, live editor and Cinema Catharsis reports.

## Live editing

When MyPro receives a live source, Cinema Catharsis can consume observations incrementally. The system may produce candidate scene, speech, action, communication or other semantic fragments while the stream is still arriving.

Live processing preserves source identity, source timestamps, exact rational time, transcoding profile, dropped ranges, discontinuities, analyzer identity and coding uncertainty.

A live detector may create a candidate fragment, but it does not silently publish, edit or classify viewer response.

## Research boundary

Cinema Catharsis is a measurement and research methodology. It can support comparative studies, content maps, temporal distributions and audience-study inputs. It must not silently convert content observations into claims about human behavior.

Every report should preserve the chain: source, observation, classification, measurement, uncertainty, interpretation.

Interpretation is a separate layer from measurement.