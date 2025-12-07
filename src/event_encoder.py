from keras import layers, Model
import keras
import numpy as np
import pandas as pd
import os
import tensorflow as tf
import metadata_manager


@keras.saving.register_keras_serializable()
def apply_masking_logic(args):
    dense_output, original_cats = args
    # create mask in order to remove dense layer biases for 0 vectors
    mask = tf.math.not_equal(original_cats, 0)
    mask = tf.cast(mask, dtype=tf.float32)
    mask = tf.expand_dims(mask, axis=-1)
    return dense_output * mask


@keras.saving.register_keras_serializable()
def sum_axis(x):
    return tf.reduce_sum(x, axis=1)


def additive_encoder(num_categories: int, latent_dim: int = 5):
    """Returns two models: the encoder itself and the whole model that can be trained (encoder + "deencoding" outputs)"""
    # input event category for each event (not a string but an ID)
    input_event = layers.Input(shape=(None,), name="input_event")
    # input the impact for each event
    input_impact = layers.Input(shape=(None, 1), name="input_impact")

    # translate the id to a vector
    emb = layers.Embedding(input_dim=num_categories, output_dim=8, mask_zero=False)(
        input_event
    )

    # add the impact
    x = layers.Concatenate(axis=-1)([emb, input_impact])

    # black box
    x = layers.Dense(16, activation="relu")(x)
    x = layers.Dense(16, activation="relu")(x)

    # merge all events

    x = layers.Lambda(apply_masking_logic)([x, input_event])
    x = layers.Lambda(sum_axis)(x)

    # output to encoded events vector in latent space. this is the output we want, which, after training, will output a vector that holds all information about the events
    latent_vector = layers.Dense(latent_dim, activation="linear", name="latent_vector")(
        x
    )

    # these layers are functions of the encoder used for training. they depend on both the category and impact of each event, so if these layers are able to obtain the information that was previously encoded we have built a successful encoder
    o_s = layers.Dense(1, activation="linear", name="o_s")(latent_vector)
    o_e = layers.Dense(num_categories, activation="exponential", name="o_e")(
        latent_vector
    )

    # trainable model
    model = Model(inputs=[input_event, input_impact], outputs=[o_s, o_e])
    # actual encoder
    encoder = Model(inputs=[input_event, input_impact], outputs=latent_vector)

    return model, encoder


def predict(
    event_data: pd.DataFrame, encoder: keras.Model, max_len: int, latent_dim: int
) -> pd.DataFrame:
    """Given an event DataFrame, returns a DataFrame with encoded events"""
    spacetime_to_events: dict[tuple[str, str], list[tuple[str, float]]] = {}

    for i, row in event_data.iterrows():
        key = (row["day"], row["barri"])
        if key not in spacetime_to_events:
            spacetime_to_events[key] = []
        spacetime_to_events[key].append((row["category"], row["impact"]))

    raw_data = list(spacetime_to_events.values())

    all_cats = set()
    for pair in raw_data:
        for cat, _ in pair:
            all_cats.add(cat)

    cat_to_id = {cat: i + 1 for i, cat in enumerate(sorted(all_cats))}

    n = len(raw_data)
    X_cat = np.zeros((n, max_len), dtype="int32")
    # the additional dimension is needed for later, the category id gets embedded and we need the extra dim for concatenation
    X_imp = np.zeros((n, max_len, 1), dtype="float32")

    # fill X_cat and X_imp
    for i, events in enumerate(raw_data):
        for j, (cat, imp) in enumerate(events):
            X_cat[i, j] = cat_to_id[cat]
            X_imp[i, j, 0] = imp

    # encode event data and output to csv
    all_encoded_events = encoder.predict(
        x={"input_event": X_cat, "input_impact": X_imp}, batch_size=1024, verbose=1
    )
    keys_list = list(spacetime_to_events.keys())

    days = [k[0] for k in keys_list]
    barris = [k[1] for k in keys_list]

    data_dict = {"day": days, "barri": barris}

    for i in range(latent_dim):
        data_dict[f"enc{i+1}"] = all_encoded_events[:, i]

    return pd.DataFrame(data_dict)


def main(manager: metadata_manager.MetadataManager) -> None:
    """Trains model to create a 5-dimensional numerical embedding of event groups aggregated by time and location,
    then saves the model and the encoded data."""
    try:
        event_data = pd.read_csv("data/all_events.csv")
    except:
        raise Exception("data/events_final.csv not found")
    spacetime_to_events: dict[tuple[str, str], list[tuple[str, float]]] = {}

    for i, row in event_data.iterrows():
        key = (row["day"], row["barri"])
        if key not in spacetime_to_events:
            spacetime_to_events[key] = []
        spacetime_to_events[key].append((row["category"], row["impact"]))

    raw_data = list(spacetime_to_events.values())

    all_cats = set()
    for pair in raw_data:
        for cat, _ in pair:
            all_cats.add(cat)

    cat_to_id = {cat: i + 1 for i, cat in enumerate(sorted(all_cats))}
    cat_amount = len(cat_to_id) + 1  # we keep 0 free

    # max_len needed to generalize shape (any group of events less are just filled with 0)
    max_len = max([len(day) for day in raw_data])

    n = len(raw_data)
    X_cat = np.zeros((n, max_len), dtype="int32")
    # the additional dimension is needed for later, the category id gets embedded and we need the extra dim for concatenation
    X_imp = np.zeros((n, max_len, 1), dtype="float32")

    # fill X_cat and X_imp
    for i, events in enumerate(raw_data):
        for j, (cat, imp) in enumerate(events):
            X_cat[i, j] = cat_to_id[cat]
            X_imp[i, j, 0] = imp

    # create targets (sum and categories)
    y_sum = np.sum(X_imp, axis=1)

    y_cats = np.zeros((n, cat_amount))
    for i in range(n):
        counts = np.bincount(X_cat[i], minlength=cat_amount)
        counts[0] = 0
        y_cats[i, :] = counts

    # create, compile and fit model
    latent_dim = 5  # dimensions we want to use to encode all event information

    model, encoder = additive_encoder(cat_amount, latent_dim)
    model.compile(
        optimizer="adam",
        loss={
            "o_s": "mse",
            "o_e": "mse",
        },
        loss_weights={"o_s": 1.0, "o_e": 5.0},
    )
    model.fit(
        x={"input_event": X_cat, "input_impact": X_imp},
        y={"o_s": y_sum, "o_e": y_cats},
        epochs=50,
        batch_size=32,
        verbose=1,
    )

    # store encoder and necessary data
    os.makedirs("models/", exist_ok=True)
    encoder.save("models/encoder.keras")
    
    manager.set("encoder_max_len", str(max_len))

    # encode event data and output to csv
    all_encoded_events = encoder.predict(
        x={"input_event": X_cat, "input_impact": X_imp}, batch_size=1024, verbose=1
    )
    keys_list = list(spacetime_to_events.keys())

    days = [k[0] for k in keys_list]
    barris = [k[1] for k in keys_list]

    data_dict = {"day": days, "barri": barris}

    for i in range(latent_dim):
        data_dict[f"enc{i+1}"] = all_encoded_events[:, i]

    pd.DataFrame(data_dict).to_csv("data/encoded_events.csv", index=None)


if __name__ == "__main__":
    main()
